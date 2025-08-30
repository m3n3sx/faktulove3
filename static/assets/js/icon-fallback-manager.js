/**
 * Icon Fallback Manager
 * Handles icon loading failures and provides fallback mechanisms
 */

class IconFallbackManager {
    constructor() {
        this.iconifyLoaded = false;
        this.remixIconLoaded = false;
        this.fallbackTimeout = 3000; // 3 seconds timeout
        this.init();
    }

    init() {
        this.checkIconifyAvailability();
        this.checkRemixIconAvailability();
        this.setupIconFallbacks();
        this.monitorIconLoading();
        this.detectFontLoadingFailure();
    }

    setupIconFallbacks() {
        // Add fallback CSS for missing icons
        const style = document.createElement('style');
        style.textContent = `
            .icon-fallback::before {
                content: '□' !important;
                font-family: Arial, sans-serif !important;
            }
            .font-fallback-mode [class^="ri-"]::before {
                content: '▢';
                font-family: Arial, sans-serif;
            }
        `;
        document.head.appendChild(style);
        
        // Process existing icons
        this.processExistingIcons();
    }

    processExistingIcons() {
        const iconElements = document.querySelectorAll('[class^="ri-"], [class*=" ri-"], iconify-icon');
        iconElements.forEach(icon => {
            if (icon.tagName === 'ICONIFY-ICON') {
                this.processIconifyIcon(icon);
            }
        });
    }

    checkIconifyAvailability() {
        // Check if Iconify is available
        if (typeof Iconify !== 'undefined' || window.Iconify) {
            this.iconifyLoaded = true;
            console.log('Iconify is available');
        } else {
            console.warn('Iconify not available, using fallbacks');
            this.enableIconifyFallbacks();
        }
    }

    checkRemixIconAvailability() {
        // Check if Remix Icon font is loaded
        const testElement = document.createElement('span');
        testElement.className = 'ri-home-line';
        testElement.style.position = 'absolute';
        testElement.style.visibility = 'hidden';
        document.body.appendChild(testElement);

        const computedStyle = window.getComputedStyle(testElement, '::before');
        const content = computedStyle.getPropertyValue('content');
        
        if (content && content !== 'none' && content !== '""') {
            this.remixIconLoaded = true;
            console.log('Remix Icon font is loaded');
        } else {
            console.warn('Remix Icon font not loaded properly');
        }

        document.body.removeChild(testElement);
    }

    enableIconifyFallbacks() {
        // Add CSS class to enable fallbacks
        document.documentElement.classList.add('iconify-fallback');
        
        // Process all iconify-icon elements
        const iconifyIcons = document.querySelectorAll('iconify-icon');
        iconifyIcons.forEach(icon => {
            this.processIconifyIcon(icon);
        });

        // Set up observer for dynamically added icons
        this.setupIconObserver();
    }

    processIconifyIcon(iconElement) {
        const iconName = iconElement.getAttribute('icon');
        if (!iconName) return;

        // Add fallback class
        iconElement.classList.add('iconify-fallback');
        
        // Set loading state
        iconElement.setAttribute('data-loading', 'true');
        
        // Remove loading state after timeout
        setTimeout(() => {
            iconElement.removeAttribute('data-loading');
        }, this.fallbackTimeout);

        // Add text fallback for critical navigation
        this.addTextFallback(iconElement, iconName);
    }

    addTextFallback(iconElement, iconName) {
        // Map of icon names to text fallbacks
        const textFallbacks = {
            'solar:home-smile-angle-outline': 'Home',
            'hugeicons:permanent-job': 'Kontrahenci',
            'hugeicons:calendar-03': 'Kalendarz',
            'hugeicons:delivery-box-01': 'Produkty',
            'hugeicons:ai-brain-04': 'OCR',
            'hugeicons:pencil-edit-02': 'Edytuj',
            'hugeicons:add-02': 'Dodaj',
            'hugeicons:workout-run': 'Wyloguj',
            'heroicons:bars-3-solid': 'Menu',
            'ion:search-outline': 'Szukaj',
            'mage:email': 'Email',
            'iconoir:bell': 'Powiadomienia',
            'lucide:power': 'Wyloguj'
        };

        const fallbackText = textFallbacks[iconName];
        if (fallbackText && !iconElement.textContent) {
            // Only add text if icon is in critical navigation
            const isInNavigation = iconElement.closest('.sidebar-menu, .navbar-header');
            if (isInNavigation) {
                iconElement.setAttribute('title', fallbackText);
                iconElement.setAttribute('aria-label', fallbackText);
            }
        }
    }

    setupIconObserver() {
        // Observer for dynamically added iconify-icon elements
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.tagName === 'ICONIFY-ICON') {
                            this.processIconifyIcon(node);
                        } else {
                            const iconifyIcons = node.querySelectorAll('iconify-icon');
                            iconifyIcons.forEach(icon => this.processIconifyIcon(icon));
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

    monitorIconLoading() {
        // Monitor for icon loading errors
        document.addEventListener('error', (event) => {
            if (event.target.tagName === 'ICONIFY-ICON') {
                console.warn('Icon loading failed:', event.target.getAttribute('icon'));
                this.handleIconError(event.target);
            }
        }, true);
    }

    handleIconError(iconElement) {
        iconElement.classList.add('icon-error');
        iconElement.setAttribute('data-error', 'true');
        
        // Try to provide a meaningful fallback
        const iconName = iconElement.getAttribute('icon');
        if (iconName) {
            console.log(`Providing fallback for failed icon: ${iconName}`);
        }
    }

    // Public method to manually trigger fallback for specific icons
    enableFallbackForIcon(iconElement) {
        if (iconElement && iconElement.tagName === 'ICONIFY-ICON') {
            this.processIconifyIcon(iconElement);
        }
    }

    // Public method to check if icons are working
    areIconsWorking() {
        return {
            iconify: this.iconifyLoaded,
            remixIcon: this.remixIconLoaded
        };
    }

    // Enhanced font loading detection
    detectFontLoadingFailure() {
        const testIcons = [
            { class: 'ri-home-line', expected: '\uea18' },
            { class: 'ri-user-line', expected: '\uf264' },
            { class: 'ri-menu-line', expected: '\uef3e' }
        ];

        let failedIcons = 0;
        
        testIcons.forEach(icon => {
            const testEl = document.createElement('span');
            testEl.className = icon.class;
            testEl.style.position = 'absolute';
            testEl.style.visibility = 'hidden';
            testEl.style.fontSize = '16px';
            document.body.appendChild(testEl);

            const computedStyle = window.getComputedStyle(testEl, '::before');
            const content = computedStyle.getPropertyValue('content');
            
            if (!content || content === 'none' || content === '""') {
                failedIcons++;
                console.warn(`Icon font failed for ${icon.class}`);
                this.enableFallbackForClass(icon.class);
            }

            document.body.removeChild(testEl);
        });

        if (failedIcons > 0) {
            console.warn(`${failedIcons} icon fonts failed to load, enabling fallbacks`);
            this.enableGlobalFontFallbacks();
        }
    }

    // Enable fallbacks for specific icon class
    enableFallbackForClass(iconClass) {
        const elements = document.querySelectorAll(`.${iconClass}`);
        elements.forEach(el => {
            el.classList.add('font-fallback');
        });
    }

    // Enable global font fallbacks
    enableGlobalFontFallbacks() {
        document.documentElement.classList.add('font-fallback-mode');
        
        const style = document.createElement('style');
        style.textContent = `
            .font-fallback-mode [class^="ri-"]::before,
            .font-fallback-mode [class*=" ri-"]::before {
                font-family: 'remixicon-fallback', Arial, sans-serif !important;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize the icon fallback manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.IconFallbackManager = new IconFallbackManager();
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading
} else {
    // DOM is already loaded
    window.IconFallbackManager = new IconFallbackManager();
}

// Add additional methods to the class
IconFallbackManager.prototype.improveIconAccessibility = function() {
    const iconElements = document.querySelectorAll('iconify-icon, [class^="ri-"], [class*=" ri-"]');
    
    iconElements.forEach(icon => {
        if (!icon.getAttribute('aria-label') && !icon.getAttribute('aria-hidden')) {
            const parent = icon.closest('a, button');
            if (parent) {
                const text = parent.textContent.trim();
                if (text && text !== icon.textContent.trim()) {
                    icon.setAttribute('aria-hidden', 'true');
                }
            } else {
                const iconClass = icon.className;
                const label = this.getIconLabel(iconClass);
                if (label) {
                    icon.setAttribute('aria-label', label);
                }
            }
        }
    });
};

IconFallbackManager.prototype.getIconLabel = function(iconClass) {
    const labels = {
        'ri-home-line': 'Strona główna',
        'ri-user-line': 'Użytkownik',
        'ri-calendar-line': 'Kalendarz',
        'ri-menu-line': 'Menu',
        'ri-search-line': 'Szukaj',
        'ri-bell-line': 'Powiadomienia',
        'ri-mail-line': 'Wiadomości',
        'ri-settings-line': 'Ustawienia',
        'ri-logout-box-line': 'Wyloguj',
        'ri-add-line': 'Dodaj',
        'ri-edit-line': 'Edytuj',
        'ri-team-line': 'Zespół',
        'ri-file-text-line': 'Dokument'
    };
    
    for (const [className, label] of Object.entries(labels)) {
        if (iconClass.includes(className)) {
            return label;
        }
    }
    return null;
};