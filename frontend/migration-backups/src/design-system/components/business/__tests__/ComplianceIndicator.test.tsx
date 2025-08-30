import React from 'react';
import { render, screen } from '@testing-library/react';
import { ComplianceIndicator } from '../ComplianceIndicator/ComplianceIndicator';

describe('ComplianceIndicator Component', () => {
  const mockRules = [
    {
      id: 'rule1',
      name: 'VAT Rate Validation',
      description: 'Correct VAT rate applied',
      status: 'compliant' as const,
      details: 'Standard 23% VAT rate applied correctly',
    },
    {
      id: 'rule2',
      name: 'NIP Validation',
      description: 'Valid NIP number format',
      status: 'warning' as const,
      details: 'NIP format is correct but not verified',
    },
    {
      id: 'rule3',
      name: 'Invoice Date',
      description: 'Invoice date within valid range',
      status: 'non-compliant' as const,
      details: 'Invoice date is in the future',
    },
  ];

  it('renders with rules correctly', () => {
    render(<ComplianceIndicator rules={mockRules} testId="compliance-indicator" />);
    
    const indicator = screen.getByTestId('compliance-indicator');
    expect(indicator).toBeInTheDocument();
    expect(screen.getByText('Zgodność z przepisami')).toBeInTheDocument();
  });

  it('determines overall status as non-compliant when any rule is non-compliant', () => {
    render(<ComplianceIndicator rules={mockRules} testId="compliance-indicator" />);
    
    const indicator = screen.getByTestId('compliance-indicator');
    expect(indicator).toHaveAttribute('data-status', 'non-compliant');
    expect(screen.getByText('Niezgodne')).toBeInTheDocument();
  });

  it('determines overall status as warning when no non-compliant but has warnings', () => {
    const warningRules = mockRules.filter(rule => rule.status !== 'non-compliant');
    render(<ComplianceIndicator rules={warningRules} testId="compliance-indicator" />);
    
    const indicator = screen.getByTestId('compliance-indicator');
    expect(indicator).toHaveAttribute('data-status', 'warning');
    expect(screen.getByText('Ostrzeżenie')).toBeInTheDocument();
  });

  it('determines overall status as compliant when all rules are compliant', () => {
    const compliantRules = [
      { ...mockRules[0], status: 'compliant' as const },
      { ...mockRules[1], status: 'compliant' as const },
      { ...mockRules[2], status: 'compliant' as const },
    ];
    render(<ComplianceIndicator rules={compliantRules} testId="compliance-indicator" />);
    
    const indicator = screen.getByTestId('compliance-indicator');
    expect(indicator).toHaveAttribute('data-status', 'compliant');
    expect(screen.getByText('Zgodne')).toBeInTheDocument();
  });

  it('shows status counts correctly', () => {
    render(<ComplianceIndicator rules={mockRules} testId="compliance-indicator" />);
    
    expect(screen.getByText('1 zgodne')).toBeInTheDocument();
    expect(screen.getByText('1 ostrzeżenia')).toBeInTheDocument();
    expect(screen.getByText('1 niezgodne')).toBeInTheDocument();
  });

  it('shows progress bar with correct percentage', () => {
    render(<ComplianceIndicator rules={mockRules} testId="compliance-indicator" />);
    
    expect(screen.getByText('1/3')).toBeInTheDocument();
    
    const progressBar = screen.getByRole('progressbar', { hidden: true });
    expect(progressBar).toHaveStyle({ width: '33.333333333333336%' });
  });

  it('shows rule details when showDetails is true', () => {
    render(<ComplianceIndicator rules={mockRules} showDetails={true} testId="compliance-indicator" />);
    
    expect(screen.getByTestId('compliance-indicator-rule-rule1')).toBeInTheDocument();
    expect(screen.getByTestId('compliance-indicator-rule-rule2')).toBeInTheDocument();
    expect(screen.getByTestId('compliance-indicator-rule-rule3')).toBeInTheDocument();
    
    expect(screen.getByText('VAT Rate Validation')).toBeInTheDocument();
    expect(screen.getByText('Correct VAT rate applied')).toBeInTheDocument();
    expect(screen.getByText('Standard 23% VAT rate applied correctly')).toBeInTheDocument();
  });

  it('hides rule details when showDetails is false', () => {
    render(<ComplianceIndicator rules={mockRules} showDetails={false} testId="compliance-indicator" />);
    
    expect(screen.queryByTestId('compliance-indicator-rule-rule1')).not.toBeInTheDocument();
    expect(screen.queryByText('VAT Rate Validation')).not.toBeInTheDocument();
  });

  it('applies small size classes', () => {
    render(<ComplianceIndicator rules={mockRules} size="sm" testId="compliance-indicator" />);
    
    const indicator = screen.getByTestId('compliance-indicator');
    expect(indicator).toHaveClass('p-2', 'text-xs');
  });

  it('applies medium size classes by default', () => {
    render(<ComplianceIndicator rules={mockRules} testId="compliance-indicator" />);
    
    const indicator = screen.getByTestId('compliance-indicator');
    expect(indicator).toHaveClass('p-3', 'text-sm');
  });

  it('applies large size classes', () => {
    render(<ComplianceIndicator rules={mockRules} size="lg" testId="compliance-indicator" />);
    
    const indicator = screen.getByTestId('compliance-indicator');
    expect(indicator).toHaveClass('p-4', 'text-base');
  });

  it('applies custom className', () => {
    render(<ComplianceIndicator rules={mockRules} className="custom-class" testId="compliance-indicator" />);
    
    const indicator = screen.getByTestId('compliance-indicator');
    expect(indicator).toHaveClass('custom-class');
  });

  it('handles empty rules array', () => {
    render(<ComplianceIndicator rules={[]} testId="compliance-indicator" />);
    
    const indicator = screen.getByTestId('compliance-indicator');
    expect(indicator).toBeInTheDocument();
    expect(screen.getByText('0/0')).toBeInTheDocument();
  });

  it('handles pending status correctly', () => {
    const pendingRules = [
      { ...mockRules[0], status: 'pending' as const },
    ];
    render(<ComplianceIndicator rules={pendingRules} testId="compliance-indicator" />);
    
    const indicator = screen.getByTestId('compliance-indicator');
    expect(indicator).toHaveAttribute('data-status', 'pending');
    expect(screen.getByText('Oczekuje')).toBeInTheDocument();
    expect(screen.getByText('1 oczekujące')).toBeInTheDocument();
  });

  it('shows correct styling for each status type', () => {
    const allStatusRules = [
      { id: '1', name: 'Rule 1', description: 'Desc 1', status: 'compliant' as const },
      { id: '2', name: 'Rule 2', description: 'Desc 2', status: 'warning' as const },
      { id: '3', name: 'Rule 3', description: 'Desc 3', status: 'non-compliant' as const },
      { id: '4', name: 'Rule 4', description: 'Desc 4', status: 'pending' as const },
    ];
    
    render(<ComplianceIndicator rules={allStatusRules} showDetails={true} testId="compliance-indicator" />);
    
    // Check that all status types are displayed
    expect(screen.getByText('1 zgodne')).toBeInTheDocument();
    expect(screen.getByText('1 ostrzeżenia')).toBeInTheDocument();
    expect(screen.getByText('1 niezgodne')).toBeInTheDocument();
    expect(screen.getByText('1 oczekujące')).toBeInTheDocument();
  });

  it('displays appropriate icons for each status', () => {
    render(<ComplianceIndicator rules={mockRules} showDetails={true} testId="compliance-indicator" />);
    
    const ruleElements = [
      screen.getByTestId('compliance-indicator-rule-rule1'),
      screen.getByTestId('compliance-indicator-rule-rule2'),
      screen.getByTestId('compliance-indicator-rule-rule3'),
    ];
    
    ruleElements.forEach(element => {
      const icon = element.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  it('calculates progress correctly with different rule combinations', () => {
    const mixedRules = [
      { id: '1', name: 'Rule 1', description: 'Desc 1', status: 'compliant' as const },
      { id: '2', name: 'Rule 2', description: 'Desc 2', status: 'compliant' as const },
      { id: '3', name: 'Rule 3', description: 'Desc 3', status: 'warning' as const },
      { id: '4', name: 'Rule 4', description: 'Desc 4', status: 'non-compliant' as const },
    ];
    
    render(<ComplianceIndicator rules={mixedRules} testId="compliance-indicator" />);
    
    expect(screen.getByText('2/4')).toBeInTheDocument();
    
    const progressBar = screen.getByRole('progressbar', { hidden: true });
    expect(progressBar).toHaveStyle({ width: '50%' });
  });

  it('handles rules without details gracefully', () => {
    const rulesWithoutDetails = [
      { id: '1', name: 'Rule 1', description: 'Desc 1', status: 'compliant' as const },
    ];
    
    render(<ComplianceIndicator rules={rulesWithoutDetails} showDetails={true} testId="compliance-indicator" />);
    
    const ruleElement = screen.getByTestId('compliance-indicator-rule-1');
    expect(ruleElement).toBeInTheDocument();
    expect(screen.getByText('Rule 1')).toBeInTheDocument();
    expect(screen.getByText('Desc 1')).toBeInTheDocument();
  });
});