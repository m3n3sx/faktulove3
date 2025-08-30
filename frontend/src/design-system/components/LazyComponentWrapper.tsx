/**
 * Lazy Component Wrapper
 * 
 * Provides Suspense wrapper and error boundary for lazy-loaded components
 */

import React, { Suspense, ComponentType, ReactNode } from 'react';
import { Typography } from './primitives/Typography/Typography';

interface LazyComponentWrapperProps {
  children: ReactNode;
  fallback?: ReactNode;
  errorFallback?: ComponentType<{ error: Error; retry: () => void }>;
  className?: string;
}

/**
 * Default loading fallback component
 */
const DefaultLoadingFallback: React.FC = () => (
  <div className="ds-flex ds-items-center ds-justify-center ds-p-4">
    <div className="ds-animate-spin ds-rounded-full ds-h-6 ds-w-6 ds-border-b-2 ds-border-primary-600"></div>
    <Typography variant="body-small" className="ds-ml-2 ds-text-muted-foreground">
      Ładowanie komponenty...
    </Typography>
  </div>
);

/**
 * Default error fallback component
 */
const DefaultErrorFallback: React.FC<{ error: Error; retry: () => void }> = ({ error, retry }) => (
  <div className="ds-p-4 ds-border ds-border-error-200 ds-rounded-md ds-bg-error-50">
    <Typography variant="body-medium" className="ds-text-error-700 ds-mb-2">
      Błąd podczas ładowania komponentu
    </Typography>
    <Typography variant="body-small" className="ds-text-error-600 ds-mb-3">
      {error.message}
    </Typography>
    <button
      onClick={retry}
      className="ds-px-3 ds-py-1 ds-text-sm ds-bg-error-600 ds-text-white ds-rounded ds-hover:bg-error-700"
    >
      Spróbuj ponownie
    </button>
  </div>
);

/**
 * Error boundary for lazy components
 */
class LazyComponentErrorBoundary extends React.Component<
  {
    children: ReactNode;
    fallback: ComponentType<{ error: Error; retry: () => void }>;
  },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Lazy component error:', error, errorInfo);
    
    // Report error to monitoring service
    if (typeof window !== 'undefined' && (window as any).reportError) {
      (window as any).reportError(error, {
        context: 'lazy-component',
        errorInfo,
      });
    }
  }

  retry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      const FallbackComponent = this.props.fallback;
      return <FallbackComponent error={this.state.error} retry={this.retry} />;
    }

    return this.props.children;
  }
}

/**
 * Lazy component wrapper with Suspense and error boundary
 */
export const LazyComponentWrapper: React.FC<LazyComponentWrapperProps> = ({
  children,
  fallback = <DefaultLoadingFallback />,
  errorFallback = DefaultErrorFallback,
  className,
}) => {
  return (
    <div className={className}>
      <LazyComponentErrorBoundary fallback={errorFallback}>
        <Suspense fallback={fallback}>
          {children}
        </Suspense>
      </LazyComponentErrorBoundary>
    </div>
  );
};

/**
 * Higher-order component for wrapping lazy components
 */
export function withLazyWrapper<P extends object>(
  LazyComponent: React.LazyExoticComponent<ComponentType<P>>,
  options: {
    fallback?: ReactNode;
    errorFallback?: ComponentType<{ error: Error; retry: () => void }>;
    displayName?: string;
  } = {}
) {
  const WrappedComponent: React.FC<P> = (props) => (
    <LazyComponentWrapper
      fallback={options.fallback}
      errorFallback={options.errorFallback}
    >
      <LazyComponent {...props} />
    </LazyComponentWrapper>
  );

  WrappedComponent.displayName = options.displayName || `LazyWrapper(${LazyComponent.displayName || 'Component'})`;

  return WrappedComponent;
}

/**
 * Polish business specific loading fallback
 */
export const PolishBusinessLoadingFallback: React.FC = () => (
  <div className="ds-flex ds-items-center ds-justify-center ds-p-4 ds-bg-polish-business-50 ds-rounded-md">
    <div className="ds-animate-pulse ds-flex ds-items-center">
      <div className="ds-h-4 ds-w-4 ds-bg-polish-business-300 ds-rounded-full ds-mr-2"></div>
      <Typography variant="body-small" className="ds-text-polish-business-700">
        Ładowanie komponentów biznesowych...
      </Typography>
    </div>
  </div>
);

/**
 * Chart loading fallback with skeleton
 */
export const ChartLoadingFallback: React.FC = () => (
  <div className="ds-p-4 ds-border ds-border-gray-200 ds-rounded-md ds-bg-gray-50">
    <div className="ds-animate-pulse">
      <div className="ds-h-4 ds-bg-gray-300 ds-rounded ds-mb-4 ds-w-1/3"></div>
      <div className="ds-space-y-2">
        <div className="ds-h-32 ds-bg-gray-300 ds-rounded"></div>
        <div className="ds-flex ds-space-x-2">
          <div className="ds-h-3 ds-bg-gray-300 ds-rounded ds-flex-1"></div>
          <div className="ds-h-3 ds-bg-gray-300 ds-rounded ds-flex-1"></div>
          <div className="ds-h-3 ds-bg-gray-300 ds-rounded ds-flex-1"></div>
        </div>
      </div>
    </div>
  </div>
);

/**
 * Form loading fallback with skeleton
 */
export const FormLoadingFallback: React.FC = () => (
  <div className="ds-p-4 ds-space-y-4">
    <div className="ds-animate-pulse ds-space-y-4">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="ds-space-y-2">
          <div className="ds-h-4 ds-bg-gray-300 ds-rounded ds-w-1/4"></div>
          <div className="ds-h-10 ds-bg-gray-300 ds-rounded"></div>
        </div>
      ))}
      <div className="ds-flex ds-space-x-2 ds-pt-4">
        <div className="ds-h-10 ds-bg-gray-300 ds-rounded ds-w-20"></div>
        <div className="ds-h-10 ds-bg-gray-300 ds-rounded ds-w-20"></div>
      </div>
    </div>
  </div>
);

/**
 * Table loading fallback with skeleton
 */
export const TableLoadingFallback: React.FC = () => (
  <div className="ds-p-4">
    <div className="ds-animate-pulse">
      <div className="ds-grid ds-grid-cols-4 ds-gap-4 ds-mb-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="ds-h-4 ds-bg-gray-300 ds-rounded"></div>
        ))}
      </div>
      {[...Array(5)].map((_, i) => (
        <div key={i} className="ds-grid ds-grid-cols-4 ds-gap-4 ds-mb-2">
          {[...Array(4)].map((_, j) => (
            <div key={j} className="ds-h-6 ds-bg-gray-200 ds-rounded"></div>
          ))}
        </div>
      ))}
    </div>
  </div>
);

export default LazyComponentWrapper;