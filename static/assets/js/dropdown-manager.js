/**
 * Dropdown Manager - Handles Bootstrap dropdown functionality
 * Ensures dropdowns work properly with proper event handling
 */

class DropdownManager {
    constructor() {
        this.initialized = false;
        this.dropdowns = [];
    }

    init() {
        if (this.initialized) return;
        
        console.log('Initializing Dropdown Manager...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupDropdowns());
        } else {
            this.setupDropdowns();
        }
        
        this.initialized = true;
    }

    setupDropdowns() {
        // Find all dropdown toggles
        const dropdownToggles = document.querySelectorAll('[data-bs-toggle="dropdown"]');
        
        dropdownToggles.forEach(toggle => {
            this.initializeDropdown(toggle);
        });

        // Setup click handlers for dropdown items
        this.setupDropdownItems();
        
        console.log(`Initialized ${dropdownToggles.length} dropdowns`);
    }

    initializeDropdown(toggle) {
        // Ensure Bootstrap is available
        if (typeof bootstrap === 'undefined') {
            console.warn('Bootstrap not available, using fallback dropdown handling');
            this.setupFallbackDropdown(toggle);
            return;
        }

        try {
            // Initialize Bootstrap dropdown
            const dropdown = new bootstrap.Dropdown(toggle);
            this.dropdowns.push(dropdown);
            
            // Add event listeners
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
            });

        } catch (error) {
            console.warn('Bootstrap dropdown initialization failed:', error);
            this.setupFallbackDropdown(toggle);
        }
    }

    setupFallbackDropdown(toggle) {
        const dropdownMenu = toggle.nextElementSibling;
        if (!dropdownMenu || !dropdownMenu.classList.contains('dropdown-menu')) {
            return;
        }

        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle dropdown visibility
            const isVisible = dropdownMenu.style.display === 'block';
            
            // Hide all other dropdowns
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.style.display = 'none';
            });
            
            // Toggle current dropdown
            dropdownMenu.style.display = isVisible ? 'none' : 'block';
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!toggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.style.display = 'none';
            }
        });
    }

    setupDropdownItems() {
        const dropdownItems = document.querySelectorAll('.dropdown-item');
        
        dropdownItems.forEach(item => {
            // Ensure dropdown items work properly
            item.addEventListener('click', (e) => {
                const href = item.getAttribute('href');
                
                if (href && href !== '#' && href !== '') {
                    // Allow normal navigation
                    return true;
                }
                
                // Prevent default for items without href
                e.preventDefault();
            });
        });
    }

    // Method to manually trigger dropdown
    toggleDropdown(toggleElement) {
        if (typeof bootstrap !== 'undefined') {
            const dropdown = bootstrap.Dropdown.getInstance(toggleElement);
            if (dropdown) {
                dropdown.toggle();
            }
        } else {
            // Fallback
            const event = new Event('click');
            toggleElement.dispatchEvent(event);
        }
    }

    // Method to close all dropdowns
    closeAllDropdowns() {
        if (typeof bootstrap !== 'undefined') {
            this.dropdowns.forEach(dropdown => {
                dropdown.hide();
            });
        } else {
            // Fallback
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.style.display = 'none';
            });
        }
    }
}

// Initialize dropdown manager
const dropdownManager = new DropdownManager();

// Auto-initialize when script loads
dropdownManager.init();

// Make available globally
window.DropdownManager = dropdownManager;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DropdownManager;
}