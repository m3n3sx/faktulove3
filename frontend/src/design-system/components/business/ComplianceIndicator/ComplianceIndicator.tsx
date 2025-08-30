import React from 'react';
import { cn } from '../../../utils/cn';
import { useThemeUtils } from '../../../providers/ThemeProvider';

export type ComplianceStatus = 'compliant' | 'warning' | 'error' | 'pending';

export interface ComplianceRule {
  id: string;
  name: string;
  description: string;
  status: ComplianceStatus;
  details?: string;
}

export interface ComplianceIndicatorProps {
  rules: ComplianceRule[];
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showDetails?: boolean;
  testId?: string;
}

const STATUS_CONFIG: Record<ComplianceStatus, {
  label: string;
  baseClasses: string;
  colorClasses: string;
  bgClasses: string;
  icon: React.ReactNode;
}> = {
  compliant: {
    label: 'Zgodne',
    baseClasses: 'text-success-700 bg-success-50 border-success-200',
    colorClasses: 'text-success-700',
    bgClasses: 'bg-success-50',
    icon: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
  warning: {
    label: 'Ostrzeżenie',
    baseClasses: 'text-warning-700 bg-warning-50 border-warning-200',
    colorClasses: 'text-warning-700',
    bgClasses: 'bg-warning-50',
    icon: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
  error: {
    label: 'Niezgodne',
    baseClasses: 'text-error-700 bg-error-50 border-error-200',
    colorClasses: 'text-error-700',
    bgClasses: 'bg-error-50',
    icon: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
  pending: {
    label: 'Oczekuje',
    baseClasses: 'text-text-secondary bg-background-muted border-border-muted',
    colorClasses: 'text-text-secondary',
    bgClasses: 'bg-background-muted',
    icon: (
      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
          clipRule="evenodd"
        />
      </svg>
    ),
  },
};

export const ComplianceIndicator: React.FC<ComplianceIndicatorProps> = ({
  rules,
  className,
  size = 'md',
  showDetails = false,
  testId,
}) => {
  const { getComplianceColor } = useThemeUtils();
  
  const getOverallStatus = (): ComplianceStatus => {
    if (rules.some(rule => rule.status === 'error')) return 'error';
    if (rules.some(rule => rule.status === 'warning')) return 'warning';
    if (rules.some(rule => rule.status === 'pending')) return 'pending';
    return 'compliant';
  };

  const overallStatus = getOverallStatus();
  const config = STATUS_CONFIG[overallStatus];

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'p-2 text-xs';
      case 'lg':
        return 'p-4 text-base';
      default:
        return 'p-3 text-sm';
    }
  };

  const getStatusCounts = () => {
    const counts = {
      compliant: 0,
      warning: 0,
      error: 0,
      pending: 0,
    };

    rules.forEach(rule => {
      counts[rule.status]++;
    });

    return counts;
  };

  const statusCounts = getStatusCounts();

  return (
    <div
      className={cn(
        'border rounded-lg transition-colors duration-200',
        getSizeClasses(),
        config.baseClasses,
        className
      )}
      style={{
        borderColor: getComplianceColor(overallStatus),
      }}
      data-testid={testId}
      data-status={overallStatus}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center">
          <div className={cn('mr-2', config.colorClasses)}>
            {config.icon}
          </div>
          <h3 className={cn('font-medium', config.colorClasses)}>
            Zgodność z przepisami
          </h3>
        </div>
        <span className={cn('text-xs font-medium', config.colorClasses)}>
          {config.label}
        </span>
      </div>

      {/* Summary */}
      <div className="flex items-center space-x-4 text-xs text-neutral-600 mb-2">
        {statusCounts.compliant > 0 && (
          <span className="flex items-center">
            <div className="w-2 h-2 bg-success-500 rounded-md-full mr-1"></div>
            {statusCounts.compliant} zgodne
          </span>
        )}
        {statusCounts.warning > 0 && (
          <span className="flex items-center">
            <div className="w-2 h-2 bg-warning-500 rounded-md-full mr-1"></div>
            {statusCounts.warning} ostrzeżenia
          </span>
        )}
        {statusCounts.error > 0 && (
          <span className="flex items-center">
            <div className="w-2 h-2 bg-error-500 rounded-full mr-1"></div>
            {statusCounts.error} niezgodne
          </span>
        )}
        {statusCounts.pending > 0 && (
          <span className="flex items-center">
            <div className="w-2 h-2 bg-neutral-400 rounded-md-full mr-1"></div>
            {statusCounts.pending} oczekujące
          </span>
        )}
      </div>

      {/* Details */}
      {showDetails && (
        <div className="space-y-2">
          {rules.map((rule) => {
            const ruleConfig = STATUS_CONFIG[rule.status];
            return (
              <div
                key={rule.id}
                className="flex items-start space-x-2 p-2 bg-white bg-opacity-50 rounded-md"
                data-testid={`${testId}-rule-${rule.id}`}
              >
                <div className={cn('mt-0.5', ruleConfig.colorClasses)}>
                  {ruleConfig.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-neutral-900">
                    {rule.name}
                  </p>
                  <p className="text-xs text-neutral-600">
                    {rule.description}
                  </p>
                  {rule.details && (
                    <p className="text-xs text-neutral-500 mt-1">
                      {rule.details}
                    </p>
                  )}
                </div>
                <span
                  className={cn(
                    'inline-flex items-center px-2 py-1 rounded-md-full text-xs font-medium',
                    ruleConfig.colorClasses,
                    ruleConfig.bgClasses
                  )}
                >
                  {ruleConfig.label}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* Progress bar */}
      <div className="mt-3">
        <div className="flex justify-between text-xs text-neutral-600 mb-1">
          <span>Postęp zgodności</span>
          <span>
            {statusCounts.compliant}/{rules.length}
          </span>
        </div>
        <div className="w-full bg-neutral-200 rounded-md-full h-2">
          <div
            className="bg-success-500 h-2 rounded-md-full transition-all duration-300"
            style={{
              width: `${(statusCounts.compliant / rules.length) * 100}%`,
            }}
          />
        </div>
      </div>
    </div>
  );
};

ComplianceIndicator.displayName = 'ComplianceIndicator';