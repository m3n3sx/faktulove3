/**
 * Lazy Loading Manager
 * 
 * Coordinates lazy loading strategy for design system components
 * based on user interactions and application state.
 */

import { ComponentGroups, LoadingStrategy, defaultLoadingStrategy, LazyLoadingPerformanceMonitor } from './lazyLoading';
import { PolishBusinessBundle } from '../components/business/lazy';
import { PatternBundle } from '../components/patterns/lazy';
import { AccessibilityBundle } from '../components/accessibility/lazy';

export class LazyLoadingManager {
  private static instance: LazyLoadingManager;
  private strategy: LoadingStrategy;
  private performanceMonitor: LazyLoadingPerformanceMonitor;
  private preloadedGroups: Set<string> = new Set();
  private userInteractionDetected = false;
  
  private constructor(strategy: LoadingStrategy = defaultLoadingStrategy) {
    this.strategy = strategy;
    this.performanceMonitor = LazyLoadingPerformanceMonitor.getInstance();
    this.setupEventListeners();
    this.initializeLoadingStrategy();
  }
  
  static getInstance(strategy?: LoadingStrategy): LazyLoadingManager {
    if (!LazyLoadingManager.instance) {
      LazyLoadingManager.instance = new LazyLoadingManager(strategy);
    }
    return LazyLoadingManager.instance;
  }
  
  /**
   * Initialize the loading strategy
   */
  private initializeLoadingStrategy(): void {
    // Preload components on idle
    this.scheduleIdlePreloading();
    
    // Set up intersection observers for on-demand loading
    this.setupIntersectionObservers();
  }
  
  /**
   * Set up event listeners for user interactions
   */
  private setupEventListeners(): void {
    // Detect first user interaction
    const interactionEvents = ['click', 'keydown', 'touchstart', 'mousemove'];
    
    const handleFirstInteraction = () => {
      if (!this.userInteractionDetected) {
        this.userInteractionDetected = true;
        this.onFirstUserInteraction();
        
        // Remove listeners after first interaction
        interactionEvents.forEach(event => {
          document.removeEventListener(event, handleFirstInteraction);
        });
      }
    };
    
    interactionEvents.forEach(event => {
      document.addEventListener(event, handleFirstInteraction, { passive: true });
    });
    
    // Detect Polish business context
    this.detectPolishBusinessContext();
    
    // Detect accessibility needs
    this.detectAccessibilityNeeds();
  }
  
  /**
   * Schedule preloading on idle
   */
  private scheduleIdlePreloading(): void {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        this.preloadIdleComponents();
      }, { timeout: 5000 });
    } else {
      // Fallback for browsers without requestIdleCallback
      setTimeout(() => {
        this.preloadIdleComponents();
      }, 1000);
    }
  }
  
  /**
   * Preload components during idle time
   */
  private async preloadIdleComponents(): Promise<void> {
    for (const group of this.strategy.preloadOnIdle) {
      if (!this.preloadedGroups.has(group)) {
        await this.preloadComponentGroup(group);
        this.preloadedGroups.add(group);
      }
    }
  }
  
  /**
   * Handle first user interaction
   */
  private async onFirstUserInteraction(): Promise<void> {
    for (const group of this.strategy.preloadOnInteraction) {
      if (!this.preloadedGroups.has(group)) {
        // Preload with slight delay to not block interaction
        setTimeout(() => {
          this.preloadComponentGroup(group);
          this.preloadedGroups.add(group);
        }, 100);
      }
    }
  }
  
  /**
   * Detect Polish business context and preload relevant components
   */
  private detectPolishBusinessContext(): void {
    // Check for Polish business indicators in the DOM
    const polishIndicators = [
      '[data-currency="PLN"]',
      '[data-locale="pl-PL"]',
      '.nip-input',
      '.vat-selector',
      '.invoice-form',
      '[lang="pl"]'
    ];
    
    const hasPolishContext = polishIndicators.some(selector => 
      document.querySelector(selector) !== null
    );
    
    if (hasPolishContext) {
      this.preloadPolishBusinessComponents();
    }
    
    // Set up mutation observer to detect dynamically added Polish content
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const element = node as Element;
            const hasPolishContent = polishIndicators.some(selector =>
              element.matches?.(selector) || element.querySelector?.(selector)
            );
            
            if (hasPolishContent) {
              this.preloadPolishBusinessComponents();
              observer.disconnect(); // Stop observing once detected
            }
          }
        });
      });
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
  
  /**
   * Detect accessibility needs and preload relevant components
   */
  private detectAccessibilityNeeds(): void {
    // Check for accessibility preferences
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches;
    const hasScreenReader = navigator.userAgent.includes('NVDA') || 
                           navigator.userAgent.includes('JAWS') ||
                           navigator.userAgent.includes('VoiceOver');
    
    // Check for keyboard navigation
    let keyboardNavigation = false;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        keyboardNavigation = true;
        this.preloadAccessibilityComponents();
        document.removeEventListener('keydown', handleKeyDown);
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    
    // Preload accessibility components if needed
    if (prefersReducedMotion || prefersHighContrast || hasScreenReader) {
      this.preloadAccessibilityComponents();
    }
  }
  
  /**
   * Set up intersection observers for on-demand loading
   */
  private setupIntersectionObservers(): void {
    // Observe chart containers
    this.observeElements('[data-chart]', () => {
      this.preloadComponentGroup(ComponentGroups.CHARTS);
    });
    
    // Observe form containers
    this.observeElements('form, [data-form]', () => {
      this.preloadComponentGroup(ComponentGroups.FORMS);
    });
    
    // Observe table containers
    this.observeElements('table, [data-table]', () => {
      PatternBundle.preloadTables();
    });
  }
  
  /**
   * Observe elements and trigger callback when they intersect
   */
  private observeElements(selector: string, callback: () => void): void {
    const elements = document.querySelectorAll(selector);
    
    if (elements.length === 0) return;
    
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            callback();
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '50px' }
    );
    
    elements.forEach(element => observer.observe(element));
  }
  
  /**
   * Preload a specific component group
   */
  private async preloadComponentGroup(group: string): Promise<void> {
    this.performanceMonitor.recordLoadStart(group);
    
    try {
      switch (group) {
        case ComponentGroups.BUSINESS:
          await this.preloadPolishBusinessComponents();
          break;
        case ComponentGroups.CHARTS:
          await PatternBundle.preloadCharts();
          break;
        case ComponentGroups.FORMS:
          await PatternBundle.preloadForms();
          break;
        case ComponentGroups.ACCESSIBILITY:
          await this.preloadAccessibilityComponents();
          break;
        case ComponentGroups.PATTERNS:
          await this.preloadPatternComponents();
          break;
        default:
          console.warn(`Unknown component group: ${group}`);
      }
      
      this.performanceMonitor.recordLoadEnd(group);
    } catch (error) {
      console.error(`Failed to preload component group ${group}:`, error);
    }
  }
  
  /**
   * Preload Polish business components
   */
  private async preloadPolishBusinessComponents(): Promise<void> {
    if (this.preloadedGroups.has(ComponentGroups.BUSINESS)) return;
    
    await PolishBusinessBundle.preload();
    this.preloadedGroups.add(ComponentGroups.BUSINESS);
  }
  
  /**
   * Preload accessibility components
   */
  private async preloadAccessibilityComponents(): Promise<void> {
    if (this.preloadedGroups.has(ComponentGroups.ACCESSIBILITY)) return;
    
    await Promise.all([
      AccessibilityBundle.preloadCore(),
      AccessibilityBundle.preloadKeyboard(),
    ]);
    this.preloadedGroups.add(ComponentGroups.ACCESSIBILITY);
  }
  
  /**
   * Preload pattern components
   */
  private async preloadPatternComponents(): Promise<void> {
    if (this.preloadedGroups.has(ComponentGroups.PATTERNS)) return;
    
    await Promise.all([
      PatternBundle.preloadForms(),
      PatternBundle.preloadTables(),
    ]);
    this.preloadedGroups.add(ComponentGroups.PATTERNS);
  }
  
  /**
   * Manually preload specific components
   */
  public async preloadComponents(components: string[]): Promise<void> {
    const preloadPromises = components.map(component => {
      switch (component) {
        case 'polish-business':
          return this.preloadPolishBusinessComponents();
        case 'accessibility':
          return this.preloadAccessibilityComponents();
        case 'charts':
          return PatternBundle.preloadCharts();
        case 'forms':
          return PatternBundle.preloadForms();
        case 'tables':
          return PatternBundle.preloadTables();
        default:
          return Promise.resolve();
      }
    });
    
    await Promise.all(preloadPromises);
  }
  
  /**
   * Get performance metrics
   */
  public getPerformanceMetrics() {
    return this.performanceMonitor.getMetrics();
  }
  
  /**
   * Update loading strategy
   */
  public updateStrategy(newStrategy: Partial<LoadingStrategy>): void {
    this.strategy = { ...this.strategy, ...newStrategy };
  }
  
  /**
   * Check if a component group is preloaded
   */
  public isPreloaded(group: string): boolean {
    return this.preloadedGroups.has(group);
  }
}

// Export singleton instance
export const lazyLoadingManager = LazyLoadingManager.getInstance();

// Initialize lazy loading on module load
if (typeof window !== 'undefined') {
  // Initialize with a small delay to allow DOM to be ready
  setTimeout(() => {
    lazyLoadingManager;
  }, 100);
}