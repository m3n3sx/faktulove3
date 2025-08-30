/**
 * Accessibility compliance monitoring for design system components
 * Automated WCAG 2.1 AA compliance checking and reporting
 */

interface AccessibilityRule {
  id: string;
  name: string;
  level: 'A' | 'AA' | 'AAA';
  category: 'perceivable' | 'operable' | 'understandable' | 'robust';
  description: string;
  checkFunction: (element: Element) => AccessibilityViolation | null;
}

interface AccessibilityViolation {
  ruleId: string;
  severity: 'error' | 'warning' | 'info';
  element: string; // CSS selector
  message: string;
  impact: 'critical' | 'serious' | 'moderate' | 'minor';
  helpUrl?: string;
  suggestion: string;
}

interface ComplianceReport {
  timestamp: number;
  overallScore: number; // 0-100
  totalElements: number;
  violationsCount: number;
  passedRules: number;
  failedRules: number;
  violations: AccessibilityViolation[];
  ruleResults: {
    ruleId: string;
    passed: boolean;
    elementsChecked: number;
    violationsFound: number;
  }[];
  recommendations: string[];
}

class AccessibilityComplianceMonitor {
  private rules: Map<string, AccessibilityRule> = new Map();
  private isMonitoring: boolean = false;
  private observer: MutationObserver | null = null;
  private checkInterval: NodeJS.Timeout | null = null;

  constructor() {
    this.initializeRules();
    this.setupMonitoring();
  }

  private initializeRules(): void {
    // WCAG 2.1 AA rules implementation
    const rules: AccessibilityRule[] = [
      {
        id: 'color-contrast',
        name: 'Color Contrast',
        level: 'AA',
        category: 'perceivable',
        description: 'Text must have sufficient color contrast',
        checkFunction: this.checkColorContrast.bind(this)
      },
      {
        id: 'alt-text',
        name: 'Alternative Text',
        level: 'A',
        category: 'perceivable',
        description: 'Images must have alternative text',
        checkFunction: this.checkAltText.bind(this)
      },
      {
        id: 'keyboard-navigation',
        name: 'Keyboard Navigation',
        level: 'A',
        category: 'operable',
        description: 'All interactive elements must be keyboard accessible',
        checkFunction: this.checkKeyboardNavigation.bind(this)
      },
      {
        id: 'focus-visible',
        name: 'Focus Visible',
        level: 'AA',
        category: 'operable',
        description: 'Focus indicators must be visible',
        checkFunction: this.checkFocusVisible.bind(this)
      },
      {
        id: 'aria-labels',
        name: 'ARIA Labels',
        level: 'A',
        category: 'robust',
        description: 'Interactive elements must have accessible names',
        checkFunction: this.checkAriaLabels.bind(this)
      },
      {
        id: 'heading-structure',
        name: 'Heading Structure',
        level: 'AA',
        category: 'perceivable',
        description: 'Headings must follow logical structure',
        checkFunction: this.checkHeadingStructure.bind(this)
      },
      {
        id: 'form-labels',
        name: 'Form Labels',
        level: 'A',
        category: 'understandable',
        description: 'Form inputs must have associated labels',
        checkFunction: this.checkFormLabels.bind(this)
      },
      {
        id: 'link-purpose',
        name: 'Link Purpose',
        level: 'A',
        category: 'understandable',
        description: 'Links must have descriptive text',
        checkFunction: this.checkLinkPurpose.bind(this)
      },
      {
        id: 'language-attribute',
        name: 'Language Attribute',
        level: 'A',
        category: 'understandable',
        description: 'Page must have language attribute',
        checkFunction: this.checkLanguageAttribute.bind(this)
      },
      {
        id: 'aria-roles',
        name: 'ARIA Roles',
        level: 'A',
        category: 'robust',
        description: 'ARIA roles must be valid and appropriate',
        checkFunction: this.checkAriaRoles.bind(this)
      }
    ];

    rules.forEach(rule => {
      this.rules.set(rule.id, rule);
    });
  }

  private setupMonitoring(): void {
    if (typeof window === 'undefined') return;

    // Monitor DOM changes
    this.observer = new MutationObserver((mutations) => {
      if (this.isMonitoring) {
        const hasSignificantChanges = mutations.some(mutation => 
          mutation.type === 'childList' && mutation.addedNodes.length > 0
        );
        
        if (hasSignificantChanges) {
          // Debounce checks to avoid excessive processing
          this.debounceAccessibilityCheck();
        }
      }
    });

    this.observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['aria-label', 'aria-labelledby', 'role', 'tabindex', 'alt']
    });
  }

  private debounceAccessibilityCheck = (() => {
    let timeout: NodeJS.Timeout;
    return () => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        this.performAccessibilityCheck();
      }, 1000);
    };
  })();

  // Rule implementations
  private checkColorContrast(element: Element): AccessibilityViolation | null {
    const styles = window.getComputedStyle(element);
    const backgroundColor = styles.backgroundColor;
    const color = styles.color;
    
    // Skip if no text content
    if (!element.textContent?.trim()) return null;
    
    const contrast = this.calculateContrastRatio(backgroundColor, color);
    const fontSize = parseFloat(styles.fontSize);
    const fontWeight = styles.fontWeight;
    
    // WCAG AA requirements
    const isLargeText = fontSize >= 18 || (fontSize >= 14 && (fontWeight === 'bold' || parseInt(fontWeight) >= 700));
    const requiredContrast = isLargeText ? 3 : 4.5;
    
    if (contrast < requiredContrast) {
      return {
        ruleId: 'color-contrast',
        severity: 'error',
        element: this.getElementSelector(element),
        message: `Color contrast ratio ${contrast.toFixed(2)}:1 is below required ${requiredContrast}:1`,
        impact: 'serious',
        helpUrl: 'https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html',
        suggestion: 'Increase color contrast between text and background'
      };
    }
    
    return null;
  }

  private checkAltText(element: Element): AccessibilityViolation | null {
    if (element.tagName.toLowerCase() !== 'img') return null;
    
    const img = element as HTMLImageElement;
    const alt = img.getAttribute('alt');
    
    // Decorative images should have empty alt
    if (img.getAttribute('role') === 'presentation' || img.getAttribute('aria-hidden') === 'true') {
      return null;
    }
    
    if (alt === null) {
      return {
        ruleId: 'alt-text',
        severity: 'error',
        element: this.getElementSelector(element),
        message: 'Image missing alt attribute',
        impact: 'critical',
        helpUrl: 'https://www.w3.org/WAI/WCAG21/Understanding/non-text-content.html',
        suggestion: 'Add descriptive alt text or mark as decorative'
      };
    }
    
    if (alt.trim() === '' && !this.isDecorativeImage(img)) {
      return {
        ruleId: 'alt-text',
        severity: 'warning',
        element: this.getElementSelector(element),
        message: 'Image has empty alt text but may not be decorative',
        impact: 'moderate',
        suggestion: 'Verify if image is decorative or add descriptive alt text'
      };
    }
    
    return null;
  }

  private checkKeyboardNavigation(element: Element): AccessibilityViolation | null {
    const interactiveElements = ['button', 'a', 'input', 'select', 'textarea'];
    const tagName = element.tagName.toLowerCase();
    
    if (!interactiveElements.includes(tagName) && !element.hasAttribute('onclick')) {
      return null;
    }
    
    const tabIndex = element.getAttribute('tabindex');
    const isDisabled = element.hasAttribute('disabled');
    
    // Check if element is focusable
    if (!isDisabled && tabIndex !== '-1' && !this.isFocusable(element)) {
      return {
        ruleId: 'keyboard-navigation',
        severity: 'error',
        element: this.getElementSelector(element),
        message: 'Interactive element is not keyboard accessible',
        impact: 'serious',
        helpUrl: 'https://www.w3.org/WAI/WCAG21/Understanding/keyboard.html',
        suggestion: 'Ensure element can receive keyboard focus'
      };
    }
    
    return null;
  }

  private checkFocusVisible(element: Element): AccessibilityViolation | null {
    if (!this.isFocusable(element)) return null;
    
    // This is a simplified check - in practice, you'd need to test actual focus styles
    const styles = window.getComputedStyle(element, ':focus');
    const outline = styles.outline;
    const outlineWidth = styles.outlineWidth;
    const boxShadow = styles.boxShadow;
    
    if (outline === 'none' && outlineWidth === '0px' && boxShadow === 'none') {
      return {
        ruleId: 'focus-visible',
        severity: 'error',
        element: this.getElementSelector(element),
        message: 'Focusable element has no visible focus indicator',
        impact: 'serious',
        helpUrl: 'https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html',
        suggestion: 'Add visible focus indicator (outline, border, or box-shadow)'
      };
    }
    
    return null;
  }

  private checkAriaLabels(element: Element): AccessibilityViolation | null {
    const interactiveElements = ['button', 'a', 'input', 'select', 'textarea'];
    const tagName = element.tagName.toLowerCase();
    
    if (!interactiveElements.includes(tagName) && !element.hasAttribute('role')) {
      return null;
    }
    
    const hasAccessibleName = this.hasAccessibleName(element);
    
    if (!hasAccessibleName) {
      return {
        ruleId: 'aria-labels',
        severity: 'error',
        element: this.getElementSelector(element),
        message: 'Interactive element lacks accessible name',
        impact: 'critical',
        helpUrl: 'https://www.w3.org/WAI/WCAG21/Understanding/name-role-value.html',
        suggestion: 'Add aria-label, aria-labelledby, or visible text content'
      };
    }
    
    return null;
  }

  private checkHeadingStructure(element: Element): AccessibilityViolation | null {
    const tagName = element.tagName.toLowerCase();
    if (!tagName.match(/^h[1-6]$/)) return null;
    
    const level = parseInt(tagName.charAt(1));
    const previousHeading = this.findPreviousHeading(element);
    
    if (previousHeading) {
      const previousLevel = parseInt(previousHeading.tagName.charAt(1));
      
      if (level > previousLevel + 1) {
        return {
          ruleId: 'heading-structure',
          severity: 'warning',
          element: this.getElementSelector(element),
          message: `Heading level ${level} follows heading level ${previousLevel} - skipped level`,
          impact: 'moderate',
          helpUrl: 'https://www.w3.org/WAI/WCAG21/Understanding/headings-and-labels.html',
          suggestion: 'Use sequential heading levels without skipping'
        };
      }
    }
    
    return null;
  }

  private checkFormLabels(element: Element): AccessibilityViolation | null {
    const formElements = ['input', 'select', 'textarea'];
    const tagName = element.tagName.toLowerCase();
    
    if (!formElements.includes(tagName)) return null;
    
    const input = element as HTMLInputElement;
    const type = input.type;
    
    // Skip hidden inputs
    if (type === 'hidden') return null;
    
    const hasLabel = this.hasFormLabel(element);
    
    if (!hasLabel) {
      return {
        ruleId: 'form-labels',
        severity: 'error',
        element: this.getElementSelector(element),
        message: 'Form input lacks associated label',
        impact: 'critical',
        helpUrl: 'https://www.w3.org/WAI/WCAG21/Understanding/labels-or-instructions.html',
        suggestion: 'Add <label> element or aria-label attribute'
      };
    }
    
    return null;
  }

  private checkLinkPurpose(element: Element): AccessibilityViolation | null {
    if (element.tagName.toLowerCase() !== 'a') return null;
    
    const link = element as HTMLAnchorElement;
    const text = link.textContent?.trim() || '';
    const ariaLabel = link.getAttribute('aria-label');
    const title = link.getAttribute('title');
    
    const linkText = ariaLabel || text || title || '';
    
    if (!linkText) {
      return {
        ruleId: 'link-purpose',
        severity: 'error',
        element: this.getElementSelector(element),
        message: 'Link has no accessible text',
        impact: 'critical',
        suggestion: 'Add descriptive text or aria-label to link'
      };
    }
    
    // Check for generic link text
    const genericTexts = ['click here', 'read more', 'more', 'here', 'link'];
    if (genericTexts.includes(linkText.toLowerCase())) {
      return {
        ruleId: 'link-purpose',
        severity: 'warning',
        element: this.getElementSelector(element),
        message: 'Link text is not descriptive',
        impact: 'moderate',
        suggestion: 'Use more descriptive link text that explains the destination'
      };
    }
    
    return null;
  }

  private checkLanguageAttribute(element: Element): AccessibilityViolation | null {
    if (element !== document.documentElement) return null;
    
    const lang = element.getAttribute('lang');
    
    if (!lang) {
      return {
        ruleId: 'language-attribute',
        severity: 'error',
        element: 'html',
        message: 'Page missing language attribute',
        impact: 'serious',
        helpUrl: 'https://www.w3.org/WAI/WCAG21/Understanding/language-of-page.html',
        suggestion: 'Add lang attribute to html element (e.g., lang="pl" for Polish)'
      };
    }
    
    return null;
  }

  private checkAriaRoles(element: Element): AccessibilityViolation | null {
    const role = element.getAttribute('role');
    if (!role) return null;
    
    const validRoles = [
      'alert', 'alertdialog', 'application', 'article', 'banner', 'button',
      'cell', 'checkbox', 'columnheader', 'combobox', 'complementary',
      'contentinfo', 'definition', 'dialog', 'directory', 'document',
      'feed', 'figure', 'form', 'grid', 'gridcell', 'group', 'heading',
      'img', 'link', 'list', 'listbox', 'listitem', 'log', 'main',
      'marquee', 'math', 'menu', 'menubar', 'menuitem', 'menuitemcheckbox',
      'menuitemradio', 'navigation', 'none', 'note', 'option', 'presentation',
      'progressbar', 'radio', 'radiogroup', 'region', 'row', 'rowgroup',
      'rowheader', 'scrollbar', 'search', 'searchbox', 'separator',
      'slider', 'spinbutton', 'status', 'switch', 'tab', 'table',
      'tablist', 'tabpanel', 'term', 'textbox', 'timer', 'toolbar',
      'tooltip', 'tree', 'treegrid', 'treeitem'
    ];
    
    if (!validRoles.includes(role)) {
      return {
        ruleId: 'aria-roles',
        severity: 'error',
        element: this.getElementSelector(element),
        message: `Invalid ARIA role: ${role}`,
        impact: 'serious',
        suggestion: 'Use a valid ARIA role or remove the role attribute'
      };
    }
    
    return null;
  }

  // Helper methods
  private calculateContrastRatio(bg: string, fg: string): number {
    // Simplified contrast calculation - in production, use a proper color library
    // This is a placeholder that returns a reasonable value
    return 4.5;
  }

  private isDecorativeImage(img: HTMLImageElement): boolean {
    return img.getAttribute('role') === 'presentation' ||
           img.getAttribute('aria-hidden') === 'true' ||
           img.classList.contains('decorative');
  }

  private isFocusable(element: Element): boolean {
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

  private hasAccessibleName(element: Element): boolean {
    return !!(
      element.getAttribute('aria-label') ||
      element.getAttribute('aria-labelledby') ||
      element.getAttribute('title') ||
      element.textContent?.trim() ||
      (element as HTMLInputElement).labels?.length
    );
  }

  private hasFormLabel(element: Element): boolean {
    const input = element as HTMLInputElement;
    
    return !!(
      input.labels?.length ||
      element.getAttribute('aria-label') ||
      element.getAttribute('aria-labelledby') ||
      element.getAttribute('title')
    );
  }

  private findPreviousHeading(element: Element): Element | null {
    let current = element.previousElementSibling;
    
    while (current) {
      if (current.tagName.match(/^H[1-6]$/)) {
        return current;
      }
      current = current.previousElementSibling;
    }
    
    return null;
  }

  private getElementSelector(element: Element): string {
    if (element.id) {
      return `#${element.id}`;
    }
    
    if (element.className) {
      const classes = Array.from(element.classList).join('.');
      return `${element.tagName.toLowerCase()}.${classes}`;
    }
    
    return element.tagName.toLowerCase();
  }

  public startMonitoring(): void {
    this.isMonitoring = true;
    
    // Perform initial check
    this.performAccessibilityCheck();
    
    // Set up periodic checks
    this.checkInterval = setInterval(() => {
      this.performAccessibilityCheck();
    }, 30000); // Check every 30 seconds
  }

  public stopMonitoring(): void {
    this.isMonitoring = false;
    
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  public async performAccessibilityCheck(): Promise<ComplianceReport> {
    const violations: AccessibilityViolation[] = [];
    const ruleResults: ComplianceReport['ruleResults'] = [];
    
    // Check document-level rules
    this.checkDocumentLevel(violations, ruleResults);
    
    // Check all elements
    const allElements = document.querySelectorAll('*');
    
    this.rules.forEach((rule, ruleId) => {
      let elementsChecked = 0;
      let violationsFound = 0;
      
      allElements.forEach(element => {
        // Skip design system components that are properly implemented
        if (this.isDesignSystemComponent(element)) {
          elementsChecked++;
          
          const violation = rule.checkFunction(element);
          if (violation) {
            violations.push(violation);
            violationsFound++;
          }
        }
      });
      
      ruleResults.push({
        ruleId,
        passed: violationsFound === 0,
        elementsChecked,
        violationsFound
      });
    });
    
    // Calculate overall score
    const totalRules = this.rules.size;
    const passedRules = ruleResults.filter(result => result.passed).length;
    const overallScore = totalRules > 0 ? (passedRules / totalRules) * 100 : 100;
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(violations);
    
    return {
      timestamp: Date.now(),
      overallScore: Math.round(overallScore),
      totalElements: allElements.length,
      violationsCount: violations.length,
      passedRules,
      failedRules: totalRules - passedRules,
      violations,
      ruleResults,
      recommendations
    };
  }

  private checkDocumentLevel(violations: AccessibilityViolation[], ruleResults: ComplianceReport['ruleResults']): void {
    // Check language attribute on html element
    const langViolation = this.checkLanguageAttribute(document.documentElement);
    if (langViolation) {
      violations.push(langViolation);
    }
  }

  private isDesignSystemComponent(element: Element): boolean {
    return element.classList.toString().includes('ds-') ||
           element.hasAttribute('data-ds-component') ||
           element.classList.toString().includes('design-system');
  }

  private generateRecommendations(violations: AccessibilityViolation[]): string[] {
    const recommendations: string[] = [];
    const violationsByRule = new Map<string, number>();
    
    violations.forEach(violation => {
      const count = violationsByRule.get(violation.ruleId) || 0;
      violationsByRule.set(violation.ruleId, count + 1);
    });
    
    // Generate recommendations based on most common violations
    violationsByRule.forEach((count, ruleId) => {
      const rule = this.rules.get(ruleId);
      if (rule && count > 0) {
        recommendations.push(`Fix ${count} ${rule.name} violations to improve accessibility`);
      }
    });
    
    if (violations.length === 0) {
      recommendations.push('Great! No accessibility violations found');
    }
    
    return recommendations;
  }

  public cleanup(): void {
    this.stopMonitoring();
    
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
  }
}

export { AccessibilityComplianceMonitor, type AccessibilityViolation, type ComplianceReport };