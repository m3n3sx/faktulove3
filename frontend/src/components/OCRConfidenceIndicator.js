import React from 'react';
import { Badge } from '../design-system/components/primitives/Badge/Badge';
import { Progress } from '../design-system/components/primitives/Progress/Progress';

const OCRConfidenceIndicator = ({ 
  confidence, 
  showProgress = false, 
  showDescription = false,
  size = 'md',
  className = '' 
}) => {
  // Determine confidence level and styling
  const getConfidenceInfo = (score) => {
    if (score >= 95) {
      return {
        level: 'excellent',
        variant: 'success',
        text: 'Doskonała',
        description: 'Dane bardzo wiarygodne, minimalne ryzyko błędów',
        color: 'text-success-700',
        bgColor: 'bg-success-50',
        borderColor: 'border-success-200',
      };
    } else if (score >= 85) {
      return {
        level: 'high',
        variant: 'success',
        text: 'Wysoka',
        description: 'Dane wiarygodne, niewielkie ryzyko błędów',
        color: 'text-success-600',
        bgColor: 'bg-success-50',
        borderColor: 'border-success-200',
      };
    } else if (score >= 70) {
      return {
        level: 'medium',
        variant: 'warning',
        text: 'Średnia',
        description: 'Zalecana weryfikacja kluczowych danych',
        color: 'text-warning-700',
        bgColor: 'bg-warning-50',
        borderColor: 'border-warning-200',
      };
    } else if (score >= 50) {
      return {
        level: 'low',
        variant: 'error',
        text: 'Niska',
        description: 'Wymagana weryfikacja większości danych',
        color: 'text-error-700',
        bgColor: 'bg-error-50',
        borderColor: 'border-error-200',
      };
    } else {
      return {
        level: 'very-low',
        variant: 'error',
        text: 'Bardzo niska',
        description: 'Wymagana dokładna weryfikacja wszystkich danych',
        color: 'text-error-800',
        bgColor: 'bg-error-100',
        borderColor: 'border-error-300',
      };
    }
  };

  if (confidence == null || confidence === undefined) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Badge variant="neutral" size={size}>
          Nieznana
        </Badge>
        {showDescription && (
          <span className="text-sm text-neutral-500">
            Brak informacji o pewności
          </span>
        )}
      </div>
    );
  }

  const info = getConfidenceInfo(confidence);
  const percentage = Math.round(confidence);

  if (showProgress) {
    return (
      <div className={`space-y-2 ${className}`}>
        <div className="flex items-center justify-between">
          <span className={`text-sm font-medium ${info.color}`}>
            Pewność OCR: {info.text}
          </span>
          <Badge variant={info.variant} size={size}>
            {percentage}%
          </Badge>
        </div>
        <Progress 
          value={confidence} 
          max={100}
          variant={info.variant}
          size={size}
        />
        {showDescription && (
          <p className={`text-xs ${info.color}`}>
            {info.description}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Badge variant={info.variant} size={size}>
        {percentage}%
      </Badge>
      {showDescription && (
        <div className="flex flex-col">
          <span className={`text-sm font-medium ${info.color}`}>
            {info.text} pewność
          </span>
          <span className={`text-xs ${info.color} opacity-75`}>
            {info.description}
          </span>
        </div>
      )}
    </div>
  );
};

// Field-specific confidence indicator
export const OCRFieldConfidence = ({ 
  fieldName, 
  confidence, 
  showLabel = true,
  size = 'xs',
  className = '' 
}) => {
  if (confidence == null || confidence === undefined) {
    return null;
  }

  const percentage = Math.round(confidence * 100);
  let variant = 'neutral';
  
  if (percentage >= 90) variant = 'success';
  else if (percentage >= 70) variant = 'warning';
  else variant = 'error';

  return (
    <div className={`inline-flex items-center gap-1 ${className}`}>
      {showLabel && (
        <span className="text-xs text-neutral-500 capitalize">
          {fieldName?.replace(/_/g, ' ')}:
        </span>
      )}
      <Badge variant={variant} size={size}>
        {percentage}%
      </Badge>
    </div>
  );
};

// Confidence comparison component
export const OCRConfidenceComparison = ({ 
  originalConfidence, 
  currentConfidence,
  className = '' 
}) => {
  const difference = currentConfidence - originalConfidence;
  const isImproved = difference > 0;
  const isWorse = difference < 0;

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="flex items-center gap-2">
        <span className="text-sm text-neutral-600">Oryginalna:</span>
        <OCRConfidenceIndicator confidence={originalConfidence} size="sm" />
      </div>
      
      <div className="flex items-center gap-2">
        <span className="text-sm text-neutral-600">Aktualna:</span>
        <OCRConfidenceIndicator confidence={currentConfidence} size="sm" />
      </div>

      {Math.abs(difference) > 1 && (
        <div className={`flex items-center gap-1 text-sm ${
          isImproved ? 'text-success-600' : isWorse ? 'text-error-600' : 'text-neutral-600'
        }`}>
          <span>
            {isImproved ? '↗' : isWorse ? '↘' : '→'}
          </span>
          <span>
            {isImproved ? '+' : ''}{difference.toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  );
};

// Confidence trend indicator
export const OCRConfidenceTrend = ({ 
  confidenceHistory = [],
  className = '' 
}) => {
  if (confidenceHistory.length < 2) {
    return null;
  }

  const latest = confidenceHistory[confidenceHistory.length - 1];
  const previous = confidenceHistory[confidenceHistory.length - 2];
  const trend = latest - previous;

  const getTrendInfo = (trend) => {
    if (Math.abs(trend) < 1) {
      return { icon: '→', color: 'text-neutral-500', text: 'Stabilna' };
    } else if (trend > 0) {
      return { icon: '↗', color: 'text-success-600', text: 'Rosnąca' };
    } else {
      return { icon: '↘', color: 'text-error-600', text: 'Spadająca' };
    }
  };

  const trendInfo = getTrendInfo(trend);

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <OCRConfidenceIndicator confidence={latest} size="sm" />
      <div className={`flex items-center gap-1 text-sm ${trendInfo.color}`}>
        <span>{trendInfo.icon}</span>
        <span>{trendInfo.text}</span>
        {Math.abs(trend) >= 1 && (
          <span className="text-xs">
            ({trend > 0 ? '+' : ''}{trend.toFixed(1)}%)
          </span>
        )}
      </div>
    </div>
  );
};

// Confidence summary for multiple fields
export const OCRConfidenceSummary = ({ 
  fieldConfidences = {},
  className = '' 
}) => {
  const confidenceValues = Object.values(fieldConfidences).filter(c => c != null);
  
  if (confidenceValues.length === 0) {
    return (
      <div className={`text-sm text-neutral-500 ${className}`}>
        Brak danych o pewności pól
      </div>
    );
  }

  const averageConfidence = confidenceValues.reduce((sum, c) => sum + c, 0) / confidenceValues.length * 100;
  const highConfidenceFields = confidenceValues.filter(c => c >= 0.9).length;
  const lowConfidenceFields = confidenceValues.filter(c => c < 0.7).length;

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center gap-4">
        <OCRConfidenceIndicator 
          confidence={averageConfidence} 
          showDescription={false}
          size="sm"
        />
        <span className="text-sm text-neutral-600">
          Średnia pewność pól
        </span>
      </div>
      
      <div className="flex gap-4 text-xs text-neutral-600">
        <span>
          Wysoka pewność: <strong>{highConfidenceFields}</strong> pól
        </span>
        <span>
          Niska pewność: <strong>{lowConfidenceFields}</strong> pól
        </span>
        <span>
          Łącznie: <strong>{confidenceValues.length}</strong> pól
        </span>
      </div>
    </div>
  );
};

export default OCRConfidenceIndicator;