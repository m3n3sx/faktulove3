/**
 * Error tracking system for design system components
 * Monitors and reports errors, performance issues, and integration problems
 */

interface DesignSystemError {
  id: string;
  timestamp: number;
  type: 'component' | 'theme' | 'accessibility' | 'performance' | 'integration';
  severity: 'low' | 'medium' | 'high' | 'critical';
  component?: string;
  message: string;
  stackTrace: string;
  userAgent: string;
  url: string;
  userId?: string;
  sessionId: string;
  context: {
    props?: Record<string, any>;
    state?: Record<string, any>;
    theme?: string;
    viewport?: { width: number; height: number };
  };
  resolved: boolean;
  resolvedAt?: number;
  resolvedBy?: string;
}

interface ErrorMetrics {
  totalErrors: number;
  errorsByType: Record<string, number>;
  errorsBySeverity: Record<string, number>;
  errorsByComponent: Record<string, number>;
  errorRate: number;
  averageResolutionTime: number;
  unresolvedErrors: number;
}

interface ErrorPattern {
  pattern: string;
  occurrences: number;
  firstSeen: number;
  lastSeen: number;
  affectedComponents: string[];
  commonContext: Record<string, any>;
}

class ErrorTracker {
  private errors: Map<string, DesignSystemError> = new Map();
  private patterns: Map<string, ErrorPattern> = new Map();
  private isTracking: boolean = false;
  private sessionId: string;
  private reportingEndpoint: string;

  constructor(reportingEndpoint: string = '/api/v1/performance-metric/') {
    this.sessionId = this.generateSessionId();
    this.reportingEndpoint = reportingEndpoint;
    this.initializeErrorTracking();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private initializeErrorTracking(): void {
    if (typeof window === 'undefined') return;

    // Global error handler
    window.addEventListener('error', this.handleGlobalError.bind(this));
    
    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', this.handleUnhandledRejection.bind(this));
    
    // React error boundary integration
    this.setupReactErrorBoundary();
    
    // Console error monitoring
    this.setupConsoleMonitoring();
  }

  private handleGlobalError(event: ErrorEvent): void {
    if (!this.isTracking) return;

    const error = this.createErrorFromEvent(event);
    this.recordError(error);
  }

  private handleUnhandledRejection(event: PromiseRejectionEvent): void {
    if (!this.isTracking) return;

    const error: DesignSystemError = {
      id: this.generateErrorId(),
      timestamp: Date.now(),
      type: 'integration',
      severity: 'high',
      message: `Unhandled Promise Rejection: ${event.reason}`,
      stackTrace: event.reason?.stack || '',
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: this.sessionId,
      context: {
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      },
      resolved: false
    };

    this.recordError(error);
  }

  private createErrorFromEvent(event: ErrorEvent): DesignSystemError {
    const component = this.extractComponentFromError(event.error);
    
    return {
      id: this.generateErrorId(),
      timestamp: Date.now(),
      type: this.classifyError(event.error, component),
      severity: this.assessSeverity(event.error, component),
      component,
      message: event.message,
      stackTrace: event.error?.stack || '',
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: this.sessionId,
      context: {
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      },
      resolved: false
    };
  }

  private extractComponentFromError(error: Error): string | undefined {
    if (!error.stack) return undefined;

    // Look for design system component names in stack trace
    const dsComponentPattern = /(?:DS|DesignSystem)([A-Z][a-zA-Z]*)/g;
    const matches = error.stack.match(dsComponentPattern);
    
    if (matches && matches.length > 0) {
      return matches[0];
    }

    // Look for common component patterns
    const componentPatterns = [
      /Button[A-Z]?/g,
      /Input[A-Z]?/g,
      /Form[A-Z]?/g,
      /Table[A-Z]?/g,
      /Card[A-Z]?/g,
      /Modal[A-Z]?/g
    ];

    for (const pattern of componentPatterns) {
      const match = error.stack.match(pattern);
      if (match) {
        return match[0];
      }
    }

    return undefined;
  }

  private classifyError(error: Error, component?: string): DesignSystemError['type'] {
    const message = error.message.toLowerCase();
    const stack = error.stack?.toLowerCase() || '';

    if (message.includes('aria') || message.includes('accessibility') || stack.includes('a11y')) {
      return 'accessibility';
    }

    if (message.includes('theme') || message.includes('css') || stack.includes('styled')) {
      return 'theme';
    }

    if (message.includes('performance') || message.includes('timeout') || message.includes('memory')) {
      return 'performance';
    }

    if (component) {
      return 'component';
    }

    return 'integration';
  }

  private assessSeverity(error: Error, component?: string): DesignSystemError['severity'] {
    const message = error.message.toLowerCase();

    // Critical errors
    if (message.includes('cannot read property') && component) {
      return 'critical';
    }

    if (message.includes('maximum call stack') || message.includes('out of memory')) {
      return 'critical';
    }

    // High severity errors
    if (message.includes('accessibility') || message.includes('aria')) {
      return 'high';
    }

    if (message.includes('theme') && component) {
      return 'high';
    }

    // Medium severity errors
    if (component && message.includes('prop')) {
      return 'medium';
    }

    if (message.includes('warning')) {
      return 'medium';
    }

    // Default to low
    return 'low';
  }

  private generateErrorId(): string {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private setupReactErrorBoundary(): void {
    // This would integrate with React error boundaries
    // For now, we'll hook into console.error to catch React errors
    const originalConsoleError = console.error;
    
    console.error = (...args) => {
      if (this.isTracking) {
        const message = args.join(' ');
        if (this.isReactError(message)) {
          this.recordReactError(message, args);
        }
      }
      
      return originalConsoleError.apply(console, args);
    };
  }

  private isReactError(message: string): boolean {
    return message.includes('React') ||
           message.includes('component') ||
           message.includes('prop') ||
           message.includes('hook');
  }

  private recordReactError(message: string, args: any[]): void {
    const component = this.extractComponentFromMessage(message);
    
    const error: DesignSystemError = {
      id: this.generateErrorId(),
      timestamp: Date.now(),
      type: 'component',
      severity: this.assessMessageSeverity(message),
      component,
      message,
      stackTrace: new Error().stack || '',
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: this.sessionId,
      context: {
        args,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      },
      resolved: false
    };

    this.recordError(error);
  }

  private extractComponentFromMessage(message: string): string | undefined {
    // Extract component name from React error messages
    const componentMatch = message.match(/in (\w+)/);
    if (componentMatch) {
      return componentMatch[1];
    }

    const dsMatch = message.match(/(DS\w+|DesignSystem\w+)/);
    if (dsMatch) {
      return dsMatch[1];
    }

    return undefined;
  }

  private assessMessageSeverity(message: string): DesignSystemError['severity'] {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('error')) {
      return 'high';
    }

    if (lowerMessage.includes('warning')) {
      return 'medium';
    }

    return 'low';
  }

  private setupConsoleMonitoring(): void {
    // Monitor console.warn for design system warnings
    const originalConsoleWarn = console.warn;
    
    console.warn = (...args) => {
      if (this.isTracking) {
        const message = args.join(' ');
        if (this.isDesignSystemWarning(message)) {
          this.recordWarning(message, args);
        }
      }
      
      return originalConsoleWarn.apply(console, args);
    };
  }

  private isDesignSystemWarning(message: string): boolean {
    return message.includes('design-system') ||
           message.includes('DS') ||
           message.includes('theme') ||
           message.includes('accessibility');
  }

  private recordWarning(message: string, args: any[]): void {
    const error: DesignSystemError = {
      id: this.generateErrorId(),
      timestamp: Date.now(),
      type: 'integration',
      severity: 'low',
      message: `Warning: ${message}`,
      stackTrace: new Error().stack || '',
      userAgent: navigator.userAgent,
      url: window.location.href,
      sessionId: this.sessionId,
      context: {
        args,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      },
      resolved: false
    };

    this.recordError(error);
  }

  public recordError(error: DesignSystemError): void {
    this.errors.set(error.id, error);
    
    // Update error patterns
    this.updateErrorPatterns(error);
    
    // Report to backend
    this.reportError(error);
    
    // Limit stored errors
    if (this.errors.size > 1000) {
      const oldestErrors = Array.from(this.errors.entries())
        .sort(([, a], [, b]) => a.timestamp - b.timestamp)
        .slice(0, 500);
      
      oldestErrors.forEach(([id]) => this.errors.delete(id));
    }
  }

  private updateErrorPatterns(error: DesignSystemError): void {
    const patternKey = this.generatePatternKey(error);
    
    let pattern = this.patterns.get(patternKey);
    if (!pattern) {
      pattern = {
        pattern: patternKey,
        occurrences: 0,
        firstSeen: error.timestamp,
        lastSeen: error.timestamp,
        affectedComponents: [],
        commonContext: {}
      };
      this.patterns.set(patternKey, pattern);
    }

    pattern.occurrences++;
    pattern.lastSeen = error.timestamp;
    
    if (error.component && !pattern.affectedComponents.includes(error.component)) {
      pattern.affectedComponents.push(error.component);
    }
  }

  private generatePatternKey(error: DesignSystemError): string {
    // Create a pattern key based on error characteristics
    const messagePattern = error.message
      .replace(/\d+/g, 'N') // Replace numbers with N
      .replace(/["'][^"']*["']/g, 'STRING') // Replace strings with STRING
      .substring(0, 100);
    
    return `${error.type}:${error.component || 'unknown'}:${messagePattern}`;
  }

  private async reportError(error: DesignSystemError): Promise<void> {
    try {
      await fetch(this.reportingEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: 'error',
          error: {
            ...error,
            context: JSON.stringify(error.context)
          }
        }),
      });
    } catch (reportingError) {
      console.warn('Failed to report error:', reportingError);
    }
  }

  public startTracking(): void {
    this.isTracking = true;
  }

  public stopTracking(): void {
    this.isTracking = false;
  }

  public resolveError(errorId: string, resolvedBy?: string): void {
    const error = this.errors.get(errorId);
    if (error) {
      error.resolved = true;
      error.resolvedAt = Date.now();
      error.resolvedBy = resolvedBy;
    }
  }

  public getErrors(filters?: {
    type?: DesignSystemError['type'];
    severity?: DesignSystemError['severity'];
    component?: string;
    resolved?: boolean;
    since?: number;
  }): DesignSystemError[] {
    let errors = Array.from(this.errors.values());

    if (filters) {
      if (filters.type) {
        errors = errors.filter(error => error.type === filters.type);
      }
      
      if (filters.severity) {
        errors = errors.filter(error => error.severity === filters.severity);
      }
      
      if (filters.component) {
        errors = errors.filter(error => error.component === filters.component);
      }
      
      if (filters.resolved !== undefined) {
        errors = errors.filter(error => error.resolved === filters.resolved);
      }
      
      if (filters.since) {
        errors = errors.filter(error => error.timestamp >= filters.since);
      }
    }

    return errors.sort((a, b) => b.timestamp - a.timestamp);
  }

  public getErrorMetrics(): ErrorMetrics {
    const errors = Array.from(this.errors.values());
    const totalErrors = errors.length;
    
    const errorsByType: Record<string, number> = {};
    const errorsBySeverity: Record<string, number> = {};
    const errorsByComponent: Record<string, number> = {};
    
    let totalResolutionTime = 0;
    let resolvedCount = 0;
    
    errors.forEach(error => {
      // Count by type
      errorsByType[error.type] = (errorsByType[error.type] || 0) + 1;
      
      // Count by severity
      errorsBySeverity[error.severity] = (errorsBySeverity[error.severity] || 0) + 1;
      
      // Count by component
      if (error.component) {
        errorsByComponent[error.component] = (errorsByComponent[error.component] || 0) + 1;
      }
      
      // Calculate resolution time
      if (error.resolved && error.resolvedAt) {
        totalResolutionTime += error.resolvedAt - error.timestamp;
        resolvedCount++;
      }
    });
    
    const averageResolutionTime = resolvedCount > 0 ? totalResolutionTime / resolvedCount : 0;
    const unresolvedErrors = errors.filter(error => !error.resolved).length;
    
    // Calculate error rate (errors per hour)
    const oldestError = errors.reduce((oldest, error) => 
      error.timestamp < oldest ? error.timestamp : oldest, Date.now()
    );
    const timeSpanHours = (Date.now() - oldestError) / (1000 * 60 * 60);
    const errorRate = timeSpanHours > 0 ? totalErrors / timeSpanHours : 0;
    
    return {
      totalErrors,
      errorsByType,
      errorsBySeverity,
      errorsByComponent,
      errorRate,
      averageResolutionTime,
      unresolvedErrors
    };
  }

  public getErrorPatterns(): ErrorPattern[] {
    return Array.from(this.patterns.values())
      .sort((a, b) => b.occurrences - a.occurrences);
  }

  public generateErrorReport(): {
    metrics: ErrorMetrics;
    recentErrors: DesignSystemError[];
    topPatterns: ErrorPattern[];
    criticalErrors: DesignSystemError[];
    recommendations: string[];
  } {
    const metrics = this.getErrorMetrics();
    const recentErrors = this.getErrors({ since: Date.now() - 24 * 60 * 60 * 1000 }); // Last 24 hours
    const topPatterns = this.getErrorPatterns().slice(0, 10);
    const criticalErrors = this.getErrors({ severity: 'critical', resolved: false });
    
    const recommendations: string[] = [];
    
    if (criticalErrors.length > 0) {
      recommendations.push(`${criticalErrors.length} critical errors need immediate attention`);
    }
    
    if (metrics.errorRate > 10) {
      recommendations.push('High error rate detected - review recent changes');
    }
    
    if (metrics.unresolvedErrors > 50) {
      recommendations.push('Many unresolved errors - prioritize error resolution');
    }
    
    const accessibilityErrors = this.getErrors({ type: 'accessibility', resolved: false });
    if (accessibilityErrors.length > 0) {
      recommendations.push(`${accessibilityErrors.length} accessibility errors affect user experience`);
    }
    
    return {
      metrics,
      recentErrors: recentErrors.slice(0, 20),
      topPatterns,
      criticalErrors,
      recommendations
    };
  }

  public cleanup(): void {
    this.stopTracking();
    this.errors.clear();
    this.patterns.clear();
  }
}

export { ErrorTracker, type DesignSystemError, type ErrorMetrics, type ErrorPattern };