/**
 * Icon Browser Compatibility Test
 * Tests icon display across different browsers and provides detailed reporting
 */

class IconBrowserTest {
    constructor() {
        this.testResults = {
            browser: this.getBrowserInfo(),
            remixIcon: { loaded: false, errors: [] },
            iconify: { loaded: false, errors: [] },
            fallbacks: { active: false, count: 0 },
            accessibility: { score: 0, issues: [] }
        };
        this.init();
    }

    init() {
        console.log('Starting icon browser compatibility test...');
        this.testRemixIconFont();
        this.testIconifyAvailability();
        this.testFallbackMechanisms();
        this.testAccessibility();
        this.generateReport();
    }

    getBrowserInfo() {
        const ua = navigator.userAgent;
        let browser = 'Unknown';
        let version = 'Unknown';

        if (ua.includes('Chrome') && !ua.includes('Edg')) {
            browser = 'Chrome';
            version = ua.match(/Chrome\/(\d+)/)?.[1] || 'Unknown';
        } else if (ua.includes('Firefox')) {
            browser = 'Firefox';
            version = ua.match(/Firefox\/(\d+)/)?.[1] || 'Unknown';
        } else if (ua.includes('Safari') && !ua.includes('Chrome')) {
            browser = 'Safari';
            version = ua.match(/Version\/(\d+)/)?.[1] || 'Unknown';
        } else if (ua.includes('Edg')) {
            browser = 'Edge';
            version = ua.match(/Edg\/(\d+)/)?.[1] || 'Unknown';
        }

        return {
            name: browser,
            version: version,
            userAgent: ua,
            platform: navigator.platform,
            language: navigator.language
        };
    }

    testRemixIconFont() {
        const testIcons = [
            'ri-home-line',
            'ri-user-line', 
            'ri-calendar-line',
            'ri-menu-line',
            'ri-search-line',
            'ri-bell-line',
            'ri-mail-line',
            'ri-settings-line'
        ];

        let loadedCount = 0;
        const errors = [];

        testIcons.forEach(iconClass => {
            const testEl = document.createElement('span');
            testEl.className = iconClass;
            testEl.style.position = 'absolute';
            testEl.style.visibility = 'hidden';
            testEl.style.fontSize = '16px';
            document.body.appendChild(testEl);

            try {
                const computedStyle = window.getComputedStyle(testEl, '::before');
                const content = computedStyle.getPropertyValue('content');
                const fontFamily = computedStyle.getPropertyValue('font-family');

                if (content && content !== 'none' && content !== '""' && fontFamily.includes('remixicon')) {
                    loadedCount++;
                } else {
                    errors.push(`${iconClass}: content="${content}", font="${fontFamily}"`);
                }
            } catch (error) {
                errors.push(`${iconClass}: ${error.message}`);
            }

            document.body.removeChild(testEl);
        });

        this.testResults.remixIcon = {
            loaded: loadedCount > testIcons.length * 0.8, // 80% success rate
            loadedCount: loadedCount,
            totalCount: testIcons.length,
            errors: errors
        };
    }

    testIconifyAvailability() {
        const iconifyAvailable = typeof Iconify !== 'undefined' || window.Iconify;
        const iconifyElements = document.querySelectorAll('iconify-icon');
        
        let renderedCount = 0;
        const errors = [];

        iconifyElements.forEach((icon, index) => {
            try {
                const rect = icon.getBoundingClientRect();
                const hasContent = icon.innerHTML.trim() !== '' || rect.width > 0 || rect.height > 0;
                
                if (hasContent) {
                    renderedCount++;
                } else {
                    errors.push(`Icon ${index}: ${icon.getAttribute('icon')} not rendered`);
                }
            } catch (error) {
                errors.push(`Icon ${index}: ${error.message}`);
            }
        });

        this.testResults.iconify = {
            loaded: iconifyAvailable,
            elementsFound: iconifyElements.length,
            renderedCount: renderedCount,
            errors: errors
        };
    }

    testFallbackMechanisms() {
        const fallbackElements = document.querySelectorAll('.iconify-fallback, .font-fallback, .icon-error');
        const hasFallbackMode = document.documentElement.classList.contains('font-fallback-mode') || 
                               document.documentElement.classList.contains('iconify-fallback');

        this.testResults.fallbacks = {
            active: hasFallbackMode || fallbackElements.length > 0,
            count: fallbackElements.length,
            mode: hasFallbackMode
        };
    }

    testAccessibility() {
        const iconElements = document.querySelectorAll('iconify-icon, [class^="ri-"], [class*=" ri-"]');
        let score = 0;
        const issues = [];

        iconElements.forEach((icon, index) => {
            const hasAriaLabel = icon.hasAttribute('aria-label');
            const hasAriaHidden = icon.hasAttribute('aria-hidden');
            const hasTitle = icon.hasAttribute('title');
            const isInInteractiveElement = icon.closest('a, button, [role="button"]');

            if (hasAriaLabel || hasAriaHidden) {
                score += 1;
            } else if (isInInteractiveElement) {
                // Interactive elements should have proper labeling
                issues.push(`Icon ${index} in interactive element lacks aria-label or aria-hidden`);
            }

            if (isInInteractiveElement && !hasAriaHidden && !hasAriaLabel && !hasTitle) {
                issues.push(`Icon ${index} in interactive element needs accessibility attributes`);
            }
        });

        this.testResults.accessibility = {
            score: iconElements.length > 0 ? Math.round((score / iconElements.length) * 100) : 100,
            totalIcons: iconElements.length,
            accessibleIcons: score,
            issues: issues
        };
    }

    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            browser: this.testResults.browser,
            summary: {
                remixIconWorking: this.testResults.remixIcon.loaded,
                iconifyWorking: this.testResults.iconify.loaded,
                fallbacksActive: this.testResults.fallbacks.active,
                accessibilityScore: this.testResults.accessibility.score
            },
            details: this.testResults
        };

        console.group('🔍 Icon Browser Compatibility Test Results');
        console.log('Browser:', report.browser.name, report.browser.version);
        console.log('Platform:', report.browser.platform);
        
        console.group('📊 Summary');
        console.log('✅ Remix Icon:', report.summary.remixIconWorking ? 'Working' : '❌ Failed');
        console.log('✅ Iconify:', report.summary.iconifyWorking ? 'Working' : '❌ Failed');
        console.log('🔄 Fallbacks:', report.summary.fallbacksActive ? 'Active' : 'Inactive');
        console.log('♿ Accessibility Score:', report.summary.accessibilityScore + '%');
        console.groupEnd();

        if (this.testResults.remixIcon.errors.length > 0) {
            console.group('❌ Remix Icon Errors');
            this.testResults.remixIcon.errors.forEach(error => console.warn(error));
            console.groupEnd();
        }

        if (this.testResults.iconify.errors.length > 0) {
            console.group('❌ Iconify Errors');
            this.testResults.iconify.errors.forEach(error => console.warn(error));
            console.groupEnd();
        }

        if (this.testResults.accessibility.issues.length > 0) {
            console.group('♿ Accessibility Issues');
            this.testResults.accessibility.issues.forEach(issue => console.warn(issue));
            console.groupEnd();
        }

        console.groupEnd();

        // Store results for potential reporting
        window.iconTestResults = report;
        
        // Dispatch custom event for other scripts to listen to
        window.dispatchEvent(new CustomEvent('iconTestComplete', { detail: report }));

        return report;
    }

    // Public method to get test results
    getResults() {
        return window.iconTestResults || this.testResults;
    }

    // Public method to re-run tests
    rerunTests() {
        this.testResults = {
            browser: this.getBrowserInfo(),
            remixIcon: { loaded: false, errors: [] },
            iconify: { loaded: false, errors: [] },
            fallbacks: { active: false, count: 0 },
            accessibility: { score: 0, issues: [] }
        };
        this.init();
    }
}

// Auto-run test when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for other scripts to load
    setTimeout(() => {
        window.IconBrowserTest = new IconBrowserTest();
    }, 2000);
});

// Also provide manual trigger
window.runIconBrowserTest = () => {
    return new IconBrowserTest();
};