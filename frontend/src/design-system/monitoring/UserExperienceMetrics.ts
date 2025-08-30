/**
 * User Experience metrics collection for design system
 * Tracks user interactions, accessibility usage, and satisfaction metrics
 */

interface UserInteraction {
  type: 'click' | 'focus' | 'keyboard' | 'touch' | 'scroll';
  component: string;
  timestamp: number;
  duration?: number;
  success: boolean;
  errorMessage?: string;
}

interface AccessibilityMetrics {
  keyboardNavigation: {
    usage: number;
    errors: number;
    averageTime: number;
  };
  screenReader: {
    detected: boolean;
    ariaErrors: number;
    missingLabels: number;
  };
  colorContrast: {
    violations: number;
    components: string[];
  };
  focusManagement: {
    trapErrors: number;
    lostFocus: number;
  };
}

interface SatisfactionMetrics {
  taskCompletionRate: number;
  averageTaskTime: number;
  errorRate: number;
  userFeedback: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

class UserExperienceMetrics {
  private interactions: UserInteraction[] = new Map();
  private accessibilityMetrics: AccessibilityMetrics;
  private satisfactionMetrics: SatisfactionMetrics;
  private sessionStartTime: number;
  private isTracking: boolean = false;

  constructor() {
    this.sessionStartTime = Date.now();
    this.initializeMetrics();
    this.setupEventListeners();
  }

  private initializeMetrics(): void {
    this.accessibilityMetrics = {
      keyboardNavigation: {
        usage: 0,
        errors: 0,
        averageTime: 0
      },
      screenReader: {
        detected: this.detectScreenReader(),
        ariaErrors: 0,
        missingLabels: 0
      },
      colorContrast: {
        violations: 0,
        components: []
      },
      focusManagement: {
        trapErrors: 0,
        lostFocus: 0
      }
    };

    this.satisfactionMetrics = {
      taskCompletionRate: 0,
      averageTaskTime: 0,
      errorRate: 0,
      userFeedback: {
        positive: 0,
        negative: 0,
        neutral: 0
      }
    };
  }

  private detectScreenReader(): boolean {
    // Check for common screen reader indicators
    return !!(
      navigator.userAgent.includes('NVDA') ||
      navigator.userAgent.includes('JAWS') ||
      navigator.userAgent.includes('VoiceOver') ||
      (window as any).speechSynthesis ||
      document.querySelector('[aria-live]')
    );
  }

  private setupEventListeners(): void {
    if (typeof window === 'undefined') return;

    // Track keyboard navigation
    document.addEventListener('keydown', this.handleKeyboardInteraction.bind(this));
    
    // Track focus management
    document.addEventListener('focusin', this.handleFocusIn.bind(this));
    document.addEventListener('focusout', this.handleFocusOut.bind(this));
    
    // Track clicks and touches
    document.addEventListener('click', this.handleClick.bind(this));
    document.addEventListener('touchstart', this.handleTouch.bind(this));
    
    // Track scroll behavior
    document.addEventListener('scroll', this.handleScroll.bind(this), { passive: true });
    
    // Track form interactions
    document.addEventListener('submit', this.handleFormSubmit.bind(this));
    document.addEventListener('input', this.handleInput.bind(this));
  }

  private handleKeyboardInteraction(event: KeyboardEvent): void {
    const target = event.target as HTMLElement;
    const component = this.getComponentName(target);
    
    if (component) {
      this.accessibilityMetrics.keyboardNavigation.usage++;
      
      this.recordInteraction({
        type: 'keyboard',
        component,
        timestamp: Date.now(),
        success: true
      });

      // Check for keyboard navigation errors
      if (event.key === 'Tab' && !this.isElementFocusable(target)) {
        this.accessibilityMetrics.keyboardNavigation.errors++;
      }
    }
  }

  private handleFocusIn(event: FocusEvent): void {
    const target = event.target as HTMLElement;
    const component = this.getComponentName(target);
    
    if (component) {
      // Check for missing ARIA labels
      if (!this.hasAccessibleLabel(target)) {
        this.accessibilityMetrics.screenReader.missingLabels++;
      }
      
      this.recordInteraction({
        type: 'focus',
        component,
        timestamp: Date.now(),
        success: true
      });
    }
  }

  private handleFocusOut(event: FocusEvent): void {
    const target = event.target as HTMLElement;
    
    // Check if focus was lost unexpectedly
    if (!event.relatedTarget && document.activeElement === document.body) {
      this.accessibilityMetrics.focusManagement.lostFocus++;
    }
  }

  private handleClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    const component = this.getComponentName(target);
    
    if (component) {
      this.recordInteraction({
        type: 'click',
        component,
        timestamp: Date.now(),
        success: true
      });
    }
  }

  private handleTouch(event: TouchEvent): void {
    const target = event.target as HTMLElement;
    const component = this.getComponentName(target);
    
    if (component) {
      this.recordInteraction({
        type: 'touch',
        component,
        timestamp: Date.now(),
        success: true
      });
    }
  }

  private handleScroll(event: Event): void {
    const target = event.target as HTMLElement;
    const component = this.getComponentName(target);
    
    if (component) {
      this.recordInteraction({
        type: 'scroll',
        component,
        timestamp: Date.now(),
        success: true
      });
    }
  }

  private handleFormSubmit(event: SubmitEvent): void {
    const form = event.target as HTMLFormElement;
    const component = this.getComponentName(form);
    
    if (component) {
      const isValid = form.checkValidity();
      
      this.recordInteraction({
        type: 'click',
        component: `${component}-submit`,
        timestamp: Date.now(),
        success: isValid,
        errorMessage: isValid ? undefined : 'Form validation failed'
      });

      if (!isValid) {
        this.satisfactionMetrics.errorRate++;
      }
    }
  }

  private handleInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    const component = this.getComponentName(input);
    
    if (component && input.validity && !input.validity.valid) {
      this.recordInteraction({
        type: 'click',
        component: `${component}-input`,
        timestamp: Date.now(),
        success: false,
        errorMessage: input.validationMessage
      });
    }
  }

  private getComponentName(element: HTMLElement): string | null {
    // Look for design system component markers
    const dsClass = Array.from(element.classList).find(cls => 
      cls.startsWith('ds-') || cls.includes('design-system')
    );
    
    if (dsClass) {
      return dsClass;
    }

    // Check data attributes
    const componentAttr = element.getAttribute('data-component') ||
                         element.getAttribute('data-testid') ||
                         element.getAttribute('data-ds-component');
    
    if (componentAttr) {
      return componentAttr;
    }

    // Check parent elements
    let parent = element.parentElement;
    while (parent && parent !== document.body) {
      const parentComponent = parent.getAttribute('data-component') ||
                             parent.getAttribute('data-ds-component');
      if (parentComponent) {
        return parentComponent;
      }
      parent = parent.parentElement;
    }

    return null;
  }

  private isElementFocusable(element: HTMLElement): boolean {
    const focusableSelectors = [
      'a[href]',
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])'
    ];

    return focusableSelectors.some(selector => element.matches(selector)) ||
           element.tabIndex >= 0;
  }

  private hasAccessibleLabel(element: HTMLElement): boolean {
    return !!(
      element.getAttribute('aria-label') ||
      element.getAttribute('aria-labelledby') ||
      element.getAttribute('title') ||
      (element as HTMLInputElement).labels?.length ||
      element.textContent?.trim()
    );
  }

  private recordInteraction(interaction: UserInteraction): void {
    if (!this.isTracking) return;

    this.interactions.push(interaction);

    // Limit interaction history
    if (this.interactions.length > 10000) {
      this.interactions = this.interactions.slice(-5000);
    }
  }

  public startTracking(): void {
    this.isTracking = true;
  }

  public stopTracking(): void {
    this.isTracking = false;
  }

  public recordTaskCompletion(taskName: string, duration: number, success: boolean): void {
    const currentRate = this.satisfactionMetrics.taskCompletionRate;
    const currentTime = this.satisfactionMetrics.averageTaskTime;
    
    // Update completion rate
    this.satisfactionMetrics.taskCompletionRate = success ? 
      (currentRate + 1) / 2 : currentRate * 0.9;
    
    // Update average task time
    this.satisfactionMetrics.averageTaskTime = (currentTime + duration) / 2;
  }

  public recordUserFeedback(sentiment: 'positive' | 'negative' | 'neutral'): void {
    this.satisfactionMetrics.userFeedback[sentiment]++;
  }

  public checkColorContrast(): Promise<void> {
    return new Promise((resolve) => {
      // This would integrate with a color contrast checking library
      const elements = document.querySelectorAll('[class*="ds-"], [data-ds-component]');
      let violations = 0;
      const violatingComponents: string[] = [];

      elements.forEach((element) => {
        const styles = window.getComputedStyle(element);
        const bgColor = styles.backgroundColor;
        const textColor = styles.color;
        
        // Simplified contrast check (would use proper algorithm in production)
        if (this.calculateContrast(bgColor, textColor) < 4.5) {
          violations++;
          const componentName = this.getComponentName(element as HTMLElement);
          if (componentName && !violatingComponents.includes(componentName)) {
            violatingComponents.push(componentName);
          }
        }
      });

      this.accessibilityMetrics.colorContrast.violations = violations;
      this.accessibilityMetrics.colorContrast.components = violatingComponents;
      
      resolve();
    });
  }

  private calculateContrast(bg: string, fg: string): number {
    // Simplified contrast calculation
    // In production, would use proper WCAG contrast algorithm
    return 4.5; // Placeholder
  }

  public getMetrics(): {
    interactions: UserInteraction[];
    accessibility: AccessibilityMetrics;
    satisfaction: SatisfactionMetrics;
    sessionDuration: number;
  } {
    return {
      interactions: [...this.interactions],
      accessibility: { ...this.accessibilityMetrics },
      satisfaction: { ...this.satisfactionMetrics },
      sessionDuration: Date.now() - this.sessionStartTime
    };
  }

  public generateUXReport(): {
    score: number;
    recommendations: string[];
    criticalIssues: string[];
    accessibilityScore: number;
  } {
    const recommendations: string[] = [];
    const criticalIssues: string[] = [];
    let score = 100;
    let accessibilityScore = 100;

    // Check accessibility metrics
    if (this.accessibilityMetrics.screenReader.missingLabels > 0) {
      criticalIssues.push(`${this.accessibilityMetrics.screenReader.missingLabels} elements missing accessible labels`);
      accessibilityScore -= 30;
      score -= 20;
    }

    if (this.accessibilityMetrics.keyboardNavigation.errors > 0) {
      recommendations.push('Improve keyboard navigation - some elements not focusable');
      accessibilityScore -= 20;
      score -= 10;
    }

    if (this.accessibilityMetrics.colorContrast.violations > 0) {
      criticalIssues.push(`${this.accessibilityMetrics.colorContrast.violations} color contrast violations`);
      accessibilityScore -= 25;
      score -= 15;
    }

    // Check satisfaction metrics
    if (this.satisfactionMetrics.errorRate > 0.1) {
      recommendations.push('High error rate detected - review form validation and UX flows');
      score -= 15;
    }

    if (this.satisfactionMetrics.taskCompletionRate < 0.8) {
      recommendations.push('Low task completion rate - simplify user workflows');
      score -= 20;
    }

    return {
      score: Math.max(0, score),
      recommendations,
      criticalIssues,
      accessibilityScore: Math.max(0, accessibilityScore)
    };
  }

  public cleanup(): void {
    this.isTracking = false;
    this.interactions = [];
  }
}

export { UserExperienceMetrics, type UserInteraction, type AccessibilityMetrics, type SatisfactionMetrics };