/**
 * Component Performance Optimizer
 * Automatically applies performance optimizations to design system components
 */

import React from 'react';
import { ComponentUsageTracker, type ComponentUsage } from '../monitoring/ComponentUsageTracker';

interface OptimizationConfig {
  enableMemoization: boolean;
  enableLazyLoading: boolean;
  enableBundleSplitting: boolean;
  enablePolishBusinessOptimizations: boolean;
  performanceThreshold: number; // ms
  usageThreshold: number; // minimum usage count for optimization
}

interface ComponentOptimization {
  componentName: string;
  optimizationType: 'memoization' | 'lazy-loading' | 'bundle-splitting' | 'polish-business';
  applied: boolean;
  performanceGain: number;
  implementation: string;
}

class ComponentPerformanceOptimizer {
  private usageTracker: ComponentUsageTracker;
  private config: OptimizationConfig;
  private appliedOptimizations: Map<string, ComponentOptimization[]> = new Map();

  constructor(config: Partial<OptimizationConfig> = {}) {
    this.config = {
      enableMemoization: true,
      enableLazyLoading: true,
      enableBundleSplitting: true,
      enablePolishBusinessOptimizations: true,
      performanceThreshold: 16, // 16ms for 60fps
      usageThreshold: 10,
      ...config
    };
    
    this.usageTracker = new ComponentUsageTracker();
  }

  public async optimizeComponents(): Promise<ComponentOptimization[]> {
    console.log('Starting component performance optimization...');
    
    const usageData = this.usageTracker.getComponentUsage() as ComponentUsage[];
    const optimizations: ComponentOptimization[] = [];
    
    for (const usage of usageData) {
      if (usage.usageCount >= this.config.usageThreshold) {
        const componentOptimizations = await this.optimizeComponent(usage);
        optimizations.push(...componentOptimizations);
      }
    }
    
    return optimizations;
  }

  private async optimizeComponent(usage: ComponentUsage): Promise<ComponentOptimization[]> {
    const optimizations: ComponentOptimization[] = [];
    
    // Apply memoization for frequently re-rendered components
    if (this.config.enableMemoization && this.shouldApplyMemoization(usage)) {
      const memoOptimization = await this.applyMemoization(usage);
      if (memoOptimization) {
        optimizations.push(memoOptimization);
      }
    }
    
    // Apply lazy loading for heavy components
    if (this.config.enableLazyLoading && this.shouldApplyLazyLoading(usage)) {
      const lazyOptimization = await this.applyLazyLoading(usage);
      if (lazyOptimization) {
        optimizations.push(lazyOptimization);
      }
    }
    
    // Apply bundle splitting for large components
    if (this.config.enableBundleSplitting && this.shouldApplyBundleSplitting(usage)) {
      const bundleOptimization = await this.applyBundleSplitting(usage);
      if (bundleOptimization) {
        optimizations.push(bundleOptimization);
      }
    }
    
    // Apply Polish business optimizations
    if (this.config.enablePolishBusinessOptimizations && this.isPolishBusinessComponent(usage)) {
      const polishOptimization = await this.applyPolishBusinessOptimizations(usage);
      if (polishOptimization) {
        optimizations.push(polishOptimization);
      }
    }
    
    // Store applied optimizations
    this.appliedOptimizations.set(usage.componentName, optimizations);
    
    return optimizations;
  }

  private shouldApplyMemoization(usage: ComponentUsage): boolean {
    // Apply memoization if component is used frequently and has many prop variations
    return usage.usageCount > 50 && usage.props.size > 3;
  }

  private shouldApplyLazyLoading(usage: ComponentUsage): boolean {
    // Apply lazy loading if component is used on few pages but has high usage
    return usage.pages.size <= 3 && usage.usageCount > 20;
  }

  private shouldApplyBundleSplitting(usage: ComponentUsage): boolean {
    // Apply bundle splitting for components with many variants or complex functionality
    return usage.variants.size > 5 || this.isComplexComponent(usage.componentName);
  }

  private isComplexComponent(componentName: string): boolean {
    const complexComponents = ['table', 'chart', 'calendar', 'editor', 'fileupload'];
    return complexComponents.some(complex => 
      componentName.toLowerCase().includes(complex)
    );
  }

  private isPolishBusinessComponent(usage: ComponentUsage): boolean {
    const polishComponents = ['nip', 'vat', 'currency', 'invoice', 'compliance'];
    return polishComponents.some(polish => 
      usage.componentName.toLowerCase().includes(polish)
    );
  }

  private async applyMemoization(usage: ComponentUsage): Promise<ComponentOptimization | null> {
    try {
      // Generate memoized component wrapper
      const memoizedComponent = this.generateMemoizedComponent(usage.componentName);
      
      return {
        componentName: usage.componentName,
        optimizationType: 'memoization',
        applied: true,
        performanceGain: this.estimatePerformanceGain('memoization', usage),
        implementation: memoizedComponent
      };
    } catch (error) {
      console.error(`Failed to apply memoization to ${usage.componentName}:`, error);
      return null;
    }
  }

  private generateMemoizedComponent(componentName: string): string {
    return `
// Optimized ${componentName} with React.memo
import React from 'react';
import { ${componentName}Base } from './${componentName}Base';

interface ${componentName}Props {
  // Component props
}

const ${componentName} = React.memo<${componentName}Props>(
  (props) => {
    return <${componentName}Base {...props} />;
  },
  (prevProps, nextProps) => {
    // Custom comparison function for optimal re-rendering
    return (
      prevProps.variant === nextProps.variant &&
      prevProps.size === nextProps.size &&
      prevProps.disabled === nextProps.disabled &&
      JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data)
    );
  }
);

${componentName}.displayName = '${componentName}';

export { ${componentName} };
`;
  }

  private async applyLazyLoading(usage: ComponentUsage): Promise<ComponentOptimization | null> {
    try {
      const lazyComponent = this.generateLazyComponent(usage.componentName);
      
      return {
        componentName: usage.componentName,
        optimizationType: 'lazy-loading',
        applied: true,
        performanceGain: this.estimatePerformanceGain('lazy-loading', usage),
        implementation: lazyComponent
      };
    } catch (error) {
      console.error(`Failed to apply lazy loading to ${usage.componentName}:`, error);
      return null;
    }
  }

  private generateLazyComponent(componentName: string): string {
    return `
// Lazy-loaded ${componentName}
import React, { Suspense, lazy } from 'react';
import { LoadingSpinner } from '../primitives/LoadingSpinner';

const ${componentName}Lazy = lazy(() => 
  import('./${componentName}').then(module => ({ default: module.${componentName} }))
);

interface ${componentName}Props {
  // Component props
}

const ${componentName}: React.FC<${componentName}Props> = (props) => {
  return (
    <Suspense fallback={<LoadingSpinner size="sm" />}>
      <${componentName}Lazy {...props} />
    </Suspense>
  );
};

export { ${componentName} };
`;
  }

  private async applyBundleSplitting(usage: ComponentUsage): Promise<ComponentOptimization | null> {
    try {
      const bundleSplitConfig = this.generateBundleSplitConfig(usage.componentName);
      
      return {
        componentName: usage.componentName,
        optimizationType: 'bundle-splitting',
        applied: true,
        performanceGain: this.estimatePerformanceGain('bundle-splitting', usage),
        implementation: bundleSplitConfig
      };
    } catch (error) {
      console.error(`Failed to apply bundle splitting to ${usage.componentName}:`, error);
      return null;
    }
  }

  private generateBundleSplitConfig(componentName: string): string {
    return `
// Webpack bundle splitting configuration for ${componentName}
module.exports = {
  optimization: {
    splitChunks: {
      cacheGroups: {
        ${componentName.toLowerCase()}: {
          test: /[\\/]${componentName}[\\/]/,
          name: 'design-system-${componentName.toLowerCase()}',
          chunks: 'all',
          priority: 10,
          reuseExistingChunk: true,
        },
      },
    },
  },
};

// Dynamic import for ${componentName}
export const load${componentName} = () => 
  import(/* webpackChunkName: "design-system-${componentName.toLowerCase()}" */ './${componentName}');
`;
  }

  private async applyPolishBusinessOptimizations(usage: ComponentUsage): Promise<ComponentOptimization | null> {
    try {
      const polishOptimization = this.generatePolishBusinessOptimization(usage.componentName);
      
      return {
        componentName: usage.componentName,
        optimizationType: 'polish-business',
        applied: true,
        performanceGain: this.estimatePerformanceGain('polish-business', usage),
        implementation: polishOptimization
      };
    } catch (error) {
      console.error(`Failed to apply Polish business optimization to ${usage.componentName}:`, error);
      return null;
    }
  }

  private generatePolishBusinessOptimization(componentName: string): string {
    if (componentName.toLowerCase().includes('nip')) {
      return this.generateNIPOptimization();
    } else if (componentName.toLowerCase().includes('currency')) {
      return this.generateCurrencyOptimization();
    } else if (componentName.toLowerCase().includes('vat')) {
      return this.generateVATOptimization();
    } else {
      return this.generateGenericPolishOptimization(componentName);
    }
  }

  private generateNIPOptimization(): string {
    return `
// Optimized NIP validation with caching
import { useMemo, useCallback } from 'react';

const nipValidationCache = new Map<string, boolean>();

export const useOptimizedNIPValidation = () => {
  const validateNIP = useCallback((nip: string): boolean => {
    // Check cache first
    if (nipValidationCache.has(nip)) {
      return nipValidationCache.get(nip)!;
    }
    
    // Perform validation
    const isValid = performNIPValidation(nip);
    
    // Cache result
    nipValidationCache.set(nip, isValid);
    
    // Limit cache size
    if (nipValidationCache.size > 1000) {
      const firstKey = nipValidationCache.keys().next().value;
      nipValidationCache.delete(firstKey);
    }
    
    return isValid;
  }, []);
  
  return { validateNIP };
};

function performNIPValidation(nip: string): boolean {
  // Optimized NIP validation algorithm
  if (!/^\\d{10}$/.test(nip)) return false;
  
  const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
  const sum = nip
    .slice(0, 9)
    .split('')
    .reduce((acc, digit, index) => acc + parseInt(digit) * weights[index], 0);
  
  const checksum = sum % 11;
  return checksum === parseInt(nip[9]);
}
`;
  }

  private generateCurrencyOptimization(): string {
    return `
// Optimized Polish currency formatting
import { useMemo } from 'react';

const currencyFormatter = new Intl.NumberFormat('pl-PL', {
  style: 'currency',
  currency: 'PLN',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export const useOptimizedCurrencyFormat = () => {
  const formatCurrency = useMemo(() => {
    const cache = new Map<number, string>();
    
    return (amount: number): string => {
      if (cache.has(amount)) {
        return cache.get(amount)!;
      }
      
      const formatted = currencyFormatter.format(amount);
      cache.set(amount, formatted);
      
      // Limit cache size
      if (cache.size > 500) {
        const firstKey = cache.keys().next().value;
        cache.delete(firstKey);
      }
      
      return formatted;
    };
  }, []);
  
  return { formatCurrency };
};
`;
  }

  private generateVATOptimization(): string {
    return `
// Optimized VAT calculations for Polish rates
import { useMemo } from 'react';

const POLISH_VAT_RATES = [0, 5, 8, 23] as const;

export const useOptimizedVATCalculation = () => {
  const calculateVAT = useMemo(() => {
    const cache = new Map<string, { net: number; vat: number; gross: number }>();
    
    return (amount: number, vatRate: number) => {
      const cacheKey = `${amount}-${vatRate}`;
      
      if (cache.has(cacheKey)) {
        return cache.get(cacheKey)!;
      }
      
      const vatMultiplier = vatRate / 100;
      const result = {
        net: amount,
        vat: amount * vatMultiplier,
        gross: amount * (1 + vatMultiplier)
      };
      
      cache.set(cacheKey, result);
      
      // Limit cache size
      if (cache.size > 1000) {
        const firstKey = cache.keys().next().value;
        cache.delete(firstKey);
      }
      
      return result;
    };
  }, []);
  
  return { calculateVAT, POLISH_VAT_RATES };
};
`;
  }

  private generateGenericPolishOptimization(componentName: string): string {
    return `
// Generic Polish business optimization for ${componentName}
import { useMemo, useCallback } from 'react';

export const usePolishBusinessOptimization = () => {
  const formatPolishDate = useCallback((date: Date): string => {
    return new Intl.DateTimeFormat('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }).format(date);
  }, []);
  
  const formatPolishNumber = useCallback((number: number): string => {
    return new Intl.NumberFormat('pl-PL').format(number);
  }, []);
  
  return {
    formatPolishDate,
    formatPolishNumber
  };
};
`;
  }

  private estimatePerformanceGain(optimizationType: string, usage: ComponentUsage): number {
    // Estimate performance gain based on optimization type and usage patterns
    switch (optimizationType) {
      case 'memoization':
        return Math.min(50, usage.usageCount * 0.5); // Up to 50% improvement
      case 'lazy-loading':
        return Math.min(30, usage.pages.size * 10); // Bundle size reduction
      case 'bundle-splitting':
        return Math.min(40, usage.variants.size * 5); // Loading time improvement
      case 'polish-business':
        return Math.min(60, usage.usageCount * 0.3); // Business logic optimization
      default:
        return 10;
    }
  }

  public getAppliedOptimizations(componentName?: string): ComponentOptimization[] {
    if (componentName) {
      return this.appliedOptimizations.get(componentName) || [];
    }
    
    const allOptimizations: ComponentOptimization[] = [];
    this.appliedOptimizations.forEach(optimizations => {
      allOptimizations.push(...optimizations);
    });
    
    return allOptimizations;
  }

  public generateOptimizationSummary(): {
    totalOptimizations: number;
    byType: Record<string, number>;
    totalPerformanceGain: number;
    recommendations: string[];
  } {
    const allOptimizations = this.getAppliedOptimizations();
    
    const byType: Record<string, number> = {};
    let totalPerformanceGain = 0;
    
    allOptimizations.forEach(opt => {
      byType[opt.optimizationType] = (byType[opt.optimizationType] || 0) + 1;
      totalPerformanceGain += opt.performanceGain;
    });
    
    const recommendations: string[] = [];
    
    if (byType['memoization'] > 5) {
      recommendations.push('Consider implementing a global memoization strategy');
    }
    
    if (byType['lazy-loading'] > 3) {
      recommendations.push('Review lazy loading implementation for consistency');
    }
    
    if (totalPerformanceGain > 200) {
      recommendations.push('Excellent optimization coverage - monitor for regressions');
    } else if (totalPerformanceGain < 50) {
      recommendations.push('More optimization opportunities available');
    }
    
    return {
      totalOptimizations: allOptimizations.length,
      byType,
      totalPerformanceGain,
      recommendations
    };
  }

  public cleanup(): void {
    this.appliedOptimizations.clear();
  }
}

export { ComponentPerformanceOptimizer, type ComponentOptimization, type OptimizationConfig };