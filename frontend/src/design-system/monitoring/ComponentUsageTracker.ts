/**
 * Component usage tracking for design system integration health monitoring
 * Tracks which components are being used, migration progress, and adoption rates
 */

interface ComponentUsage {
  componentName: string;
  usageCount: number;
  firstUsed: number;
  lastUsed: number;
  pages: Set<string>;
  variants: Set<string>;
  props: Map<string, number>;
  errors: ComponentError[];
}

interface ComponentError {
  timestamp: number;
  error: string;
  stackTrace: string;
  props: Record<string, any>;
  page: string;
}

interface MigrationStatus {
  componentName: string;
  oldComponentUsage: number;
  newComponentUsage: number;
  migrationProgress: number; // 0-100%
  lastMigrationActivity: number;
  blockers: string[];
}

interface IntegrationHealth {
  overallScore: number;
  componentAdoption: number;
  migrationProgress: number;
  errorRate: number;
  performanceScore: number;
  accessibilityScore: number;
}

class ComponentUsageTracker {
  private usage: Map<string, ComponentUsage> = new Map();
  private migrationStatus: Map<string, MigrationStatus> = new Map();
  private isTracking: boolean = false;
  private observer: MutationObserver | null = null;

  constructor() {
    this.initializeTracking();
  }

  private initializeTracking(): void {
    if (typeof window === 'undefined') return;

    // Track component usage through DOM observation
    this.setupDOMObserver();
    
    // Track React component usage through DevTools hook
    this.setupReactTracking();
    
    // Track page changes for usage context
    this.setupPageTracking();
  }

  private setupDOMObserver(): void {
    if ('MutationObserver' in window) {
      this.observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === 'childList') {
            mutation.addedNodes.forEach((node) => {
              if (node.nodeType === Node.ELEMENT_NODE) {
                this.scanForDesignSystemComponents(node as Element);
              }
            });
          }
        });
      });

      this.observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'data-component', 'data-ds-component']
      });
    }
  }

  private scanForDesignSystemComponents(element: Element): void {
    // Check if element itself is a design system component
    const componentName = this.getComponentName(element);
    if (componentName) {
      this.recordComponentUsage(componentName, element);
    }

    // Check child elements
    const dsElements = element.querySelectorAll('[class*="ds-"], [data-ds-component], [data-component]');
    dsElements.forEach((el) => {
      const childComponentName = this.getComponentName(el);
      if (childComponentName) {
        this.recordComponentUsage(childComponentName, el);
      }
    });
  }

  private getComponentName(element: Element): string | null {
    // Check for design system class names
    const classList = Array.from(element.classList);
    const dsClass = classList.find(cls => 
      cls.startsWith('ds-') || 
      cls.includes('design-system') ||
      cls.startsWith('DS')
    );

    if (dsClass) {
      return this.normalizeComponentName(dsClass);
    }

    // Check data attributes
    const componentAttr = element.getAttribute('data-ds-component') ||
                         element.getAttribute('data-component');
    
    if (componentAttr) {
      return this.normalizeComponentName(componentAttr);
    }

    return null;
  }

  private normalizeComponentName(name: string): string {
    // Normalize component names to consistent format
    return name
      .replace(/^ds-/, '')
      .replace(/^DS/, '')
      .replace(/-/g, '')
      .toLowerCase();
  }

  private recordComponentUsage(componentName: string, element: Element): void {
    if (!this.isTracking) return;

    const currentPage = window.location.pathname;
    const timestamp = Date.now();

    let usage = this.usage.get(componentName);
    if (!usage) {
      usage = {
        componentName,
        usageCount: 0,
        firstUsed: timestamp,
        lastUsed: timestamp,
        pages: new Set(),
        variants: new Set(),
        props: new Map(),
        errors: []
      };
      this.usage.set(componentName, usage);
    }

    usage.usageCount++;
    usage.lastUsed = timestamp;
    usage.pages.add(currentPage);

    // Track variants (size, color, etc.)
    const variant = this.extractVariant(element);
    if (variant) {
      usage.variants.add(variant);
    }

    // Track common props
    this.trackElementProps(element, usage);
  }

  private extractVariant(element: Element): string | null {
    const classList = Array.from(element.classList);
    
    // Look for variant classes
    const variantClass = classList.find(cls => 
      cls.includes('-primary') ||
      cls.includes('-secondary') ||
      cls.includes('-large') ||
      cls.includes('-small') ||
      cls.includes('-success') ||
      cls.includes('-error') ||
      cls.includes('-warning')
    );

    return variantClass || null;
  }

  private trackElementProps(element: Element, usage: ComponentUsage): void {
    // Track common attributes as "props"
    const attributes = ['disabled', 'required', 'readonly', 'aria-label', 'role'];
    
    attributes.forEach(attr => {
      if (element.hasAttribute(attr)) {
        const count = usage.props.get(attr) || 0;
        usage.props.set(attr, count + 1);
      }
    });
  }

  private setupReactTracking(): void {
    // Hook into React DevTools if available
    if (typeof window !== 'undefined' && (window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__) {
      const hook = (window as any).__REACT_DEVTOOLS_GLOBAL_HOOK__;
      
      if (hook.onCommitFiberRoot) {
        const originalOnCommit = hook.onCommitFiberRoot;
        hook.onCommitFiberRoot = (id: any, root: any) => {
          this.trackReactComponents(root);
          return originalOnCommit(id, root);
        };
      }
    }
  }

  private trackReactComponents(root: any): void {
    if (root && root.current) {
      this.traverseReactTree(root.current);
    }
  }

  private traverseReactTree(fiber: any): void {
    if (fiber.type && fiber.type.name) {
      const componentName = fiber.type.name;
      
      // Check if it's a design system component
      if (this.isDesignSystemComponent(componentName)) {
        this.recordReactComponentUsage(componentName, fiber);
      }
    }

    // Traverse children
    let child = fiber.child;
    while (child) {
      this.traverseReactTree(child);
      child = child.sibling;
    }
  }

  private isDesignSystemComponent(componentName: string): boolean {
    return componentName.startsWith('DS') ||
           componentName.includes('DesignSystem') ||
           componentName.startsWith('Button') ||
           componentName.startsWith('Input') ||
           componentName.startsWith('Card') ||
           componentName.startsWith('Table');
  }

  private recordReactComponentUsage(componentName: string, fiber: any): void {
    const normalizedName = this.normalizeComponentName(componentName);
    
    // Record usage similar to DOM tracking
    this.recordComponentUsage(normalizedName, document.createElement('div'));
    
    // Track React-specific props
    if (fiber.memoizedProps) {
      this.trackReactProps(normalizedName, fiber.memoizedProps);
    }
  }

  private trackReactProps(componentName: string, props: any): void {
    const usage = this.usage.get(componentName);
    if (!usage) return;

    Object.keys(props).forEach(propName => {
      if (propName !== 'children') {
        const count = usage.props.get(propName) || 0;
        usage.props.set(propName, count + 1);
      }
    });
  }

  private setupPageTracking(): void {
    // Track page changes for context
    let currentPage = window.location.pathname;
    
    const trackPageChange = () => {
      const newPage = window.location.pathname;
      if (newPage !== currentPage) {
        currentPage = newPage;
        // Reset page-specific tracking if needed
      }
    };

    // Listen for navigation events
    window.addEventListener('popstate', trackPageChange);
    
    // Override pushState and replaceState to catch programmatic navigation
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;
    
    history.pushState = function(...args) {
      originalPushState.apply(history, args);
      trackPageChange();
    };
    
    history.replaceState = function(...args) {
      originalReplaceState.apply(history, args);
      trackPageChange();
    };
  }

  public startTracking(): void {
    this.isTracking = true;
    
    // Initial scan of existing components
    this.scanForDesignSystemComponents(document.body);
  }

  public stopTracking(): void {
    this.isTracking = false;
    
    if (this.observer) {
      this.observer.disconnect();
    }
  }

  public recordComponentError(componentName: string, error: Error, props?: any): void {
    const usage = this.usage.get(componentName);
    if (usage) {
      usage.errors.push({
        timestamp: Date.now(),
        error: error.message,
        stackTrace: error.stack || '',
        props: props || {},
        page: window.location.pathname
      });
    }
  }

  public trackMigration(componentName: string, oldUsage: number, newUsage: number): void {
    const existing = this.migrationStatus.get(componentName);
    const progress = oldUsage > 0 ? (newUsage / (oldUsage + newUsage)) * 100 : 100;
    
    if (existing) {
      existing.oldComponentUsage = oldUsage;
      existing.newComponentUsage = newUsage;
      existing.migrationProgress = progress;
      existing.lastMigrationActivity = Date.now();
    } else {
      this.migrationStatus.set(componentName, {
        componentName,
        oldComponentUsage: oldUsage,
        newComponentUsage: newUsage,
        migrationProgress: progress,
        lastMigrationActivity: Date.now(),
        blockers: []
      });
    }
  }

  public addMigrationBlocker(componentName: string, blocker: string): void {
    const migration = this.migrationStatus.get(componentName);
    if (migration && !migration.blockers.includes(blocker)) {
      migration.blockers.push(blocker);
    }
  }

  public getComponentUsage(componentName?: string): ComponentUsage | ComponentUsage[] {
    if (componentName) {
      return this.usage.get(componentName) || this.createEmptyUsage(componentName);
    }
    
    return Array.from(this.usage.values());
  }

  private createEmptyUsage(componentName: string): ComponentUsage {
    return {
      componentName,
      usageCount: 0,
      firstUsed: 0,
      lastUsed: 0,
      pages: new Set(),
      variants: new Set(),
      props: new Map(),
      errors: []
    };
  }

  public getMigrationStatus(): MigrationStatus[] {
    return Array.from(this.migrationStatus.values());
  }

  public calculateIntegrationHealth(): IntegrationHealth {
    const allUsage = Array.from(this.usage.values());
    const allMigrations = Array.from(this.migrationStatus.values());
    
    // Calculate component adoption (% of pages using design system)
    const totalPages = new Set();
    allUsage.forEach(usage => {
      usage.pages.forEach(page => totalPages.add(page));
    });
    const componentAdoption = totalPages.size > 0 ? 
      (allUsage.length / totalPages.size) * 100 : 0;
    
    // Calculate migration progress
    const migrationProgress = allMigrations.length > 0 ?
      allMigrations.reduce((sum, m) => sum + m.migrationProgress, 0) / allMigrations.length : 100;
    
    // Calculate error rate
    const totalErrors = allUsage.reduce((sum, usage) => sum + usage.errors.length, 0);
    const totalUsage = allUsage.reduce((sum, usage) => sum + usage.usageCount, 0);
    const errorRate = totalUsage > 0 ? (totalErrors / totalUsage) * 100 : 0;
    
    // Calculate overall score
    const overallScore = (
      (componentAdoption * 0.3) +
      (migrationProgress * 0.3) +
      ((100 - errorRate) * 0.2) +
      (80 * 0.2) // Placeholder for performance and accessibility scores
    );
    
    return {
      overallScore: Math.round(overallScore),
      componentAdoption: Math.round(componentAdoption),
      migrationProgress: Math.round(migrationProgress),
      errorRate: Math.round(errorRate * 100) / 100,
      performanceScore: 80, // Would be calculated from performance metrics
      accessibilityScore: 85 // Would be calculated from accessibility metrics
    };
  }

  public generateUsageReport(): {
    summary: IntegrationHealth;
    topComponents: ComponentUsage[];
    migrationStatus: MigrationStatus[];
    recentErrors: ComponentError[];
    recommendations: string[];
  } {
    const summary = this.calculateIntegrationHealth();
    const allUsage = Array.from(this.usage.values());
    const allMigrations = Array.from(this.migrationStatus.values());
    
    // Get top used components
    const topComponents = allUsage
      .sort((a, b) => b.usageCount - a.usageCount)
      .slice(0, 10);
    
    // Get recent errors
    const recentErrors: ComponentError[] = [];
    allUsage.forEach(usage => {
      recentErrors.push(...usage.errors);
    });
    recentErrors.sort((a, b) => b.timestamp - a.timestamp);
    
    // Generate recommendations
    const recommendations: string[] = [];
    
    if (summary.componentAdoption < 50) {
      recommendations.push('Low component adoption - increase design system usage');
    }
    
    if (summary.migrationProgress < 80) {
      recommendations.push('Migration incomplete - prioritize remaining component migrations');
    }
    
    if (summary.errorRate > 5) {
      recommendations.push('High error rate - review component implementations');
    }
    
    const staleComponents = allUsage.filter(usage => 
      Date.now() - usage.lastUsed > 7 * 24 * 60 * 60 * 1000 // 7 days
    );
    
    if (staleComponents.length > 0) {
      recommendations.push(`${staleComponents.length} components haven't been used recently`);
    }
    
    return {
      summary,
      topComponents,
      migrationStatus: allMigrations,
      recentErrors: recentErrors.slice(0, 20),
      recommendations
    };
  }

  public cleanup(): void {
    this.stopTracking();
    this.usage.clear();
    this.migrationStatus.clear();
  }
}

export { ComponentUsageTracker, type ComponentUsage, type MigrationStatus, type IntegrationHealth };