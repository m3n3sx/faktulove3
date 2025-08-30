
        // Accessibility improvements for FaktuLove
        class AccessibilityManager {
            constructor() {
                this.init();
            }
            
            init() {
                this.addSkipLinks();
                this.improveKeyboardNavigation();
                this.addAriaLiveRegions();
                this.enhanceFocusManagement();
                this.addScreenReaderSupport();
            }
            
            addSkipLinks() {
                // Add skip to main content link
                const skipLink = document.createElement('a');
                skipLink.href = '#main-content';
                skipLink.className = 'skip-link';
                skipLink.textContent = 'Przejdź do głównej treści';
                skipLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    const mainContent = document.getElementById('main-content') || 
                                      document.querySelector('main') ||
                                      document.querySelector('.dashboard-main-body');
                    if (mainContent) {
                        mainContent.focus();
                        mainContent.scrollIntoView();
                    }
                });
                
                document.body.insertBefore(skipLink, document.body.firstChild);
            }
            
            improveKeyboardNavigation() {
                // Make all interactive elements keyboard accessible
                document.querySelectorAll('[onclick], .clickable').forEach(element => {
                    if (!element.hasAttribute('tabindex')) {
                        element.setAttribute('tabindex', '0');
                    }
                    
                    if (!element.hasAttribute('role')) {
                        element.setAttribute('role', 'button');
                    }
                    
                    element.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            element.click();
                        }
                    });
                });
                
                // Improve table navigation
                document.querySelectorAll('table').forEach(table => {
                    table.setAttribute('role', 'table');
                    
                    const headers = table.querySelectorAll('th');
                    headers.forEach((header, index) => {
                        header.setAttribute('scope', 'col');
                        header.id = header.id || `header-${index}`;
                    });
                    
                    const cells = table.querySelectorAll('td');
                    cells.forEach(cell => {
                        const headerIndex = Array.from(cell.parentNode.children).indexOf(cell);
                        const header = headers[headerIndex];
                        if (header) {
                            cell.setAttribute('headers', header.id);
                        }
                    });
                });
            }
            
            addAriaLiveRegions() {
                // Add live region for status updates
                const liveRegion = document.createElement('div');
                liveRegion.id = 'aria-live-region';
                liveRegion.setAttribute('aria-live', 'polite');
                liveRegion.setAttribute('aria-atomic', 'true');
                liveRegion.className = 'sr-only';
                document.body.appendChild(liveRegion);
                
                // Add alert region for important messages
                const alertRegion = document.createElement('div');
                alertRegion.id = 'aria-alert-region';
                alertRegion.setAttribute('aria-live', 'assertive');
                alertRegion.setAttribute('role', 'alert');
                alertRegion.className = 'sr-only';
                document.body.appendChild(alertRegion);
            }
            
            enhanceFocusManagement() {
                // Manage focus for modals
                document.addEventListener('shown.bs.modal', (e) => {
                    const modal = e.target;
                    const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                    if (firstFocusable) {
                        firstFocusable.focus();
                    }
                });
                
                // Trap focus in modals
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Tab') {
                        const activeModal = document.querySelector('.modal.show');
                        if (activeModal) {
                            this.trapFocus(e, activeModal);
                        }
                    }
                });
            }
            
            trapFocus(e, container) {
                const focusableElements = container.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                
                const firstFocusable = focusableElements[0];
                const lastFocusable = focusableElements[focusableElements.length - 1];
                
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        e.preventDefault();
                        lastFocusable.focus();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        e.preventDefault();
                        firstFocusable.focus();
                    }
                }
            }
            
            addScreenReaderSupport() {
                // Add screen reader announcements for dynamic content
                window.announceToScreenReader = (message, priority = 'polite') => {
                    const region = priority === 'assertive' ? 
                        document.getElementById('aria-alert-region') :
                        document.getElementById('aria-live-region');
                    
                    if (region) {
                        region.textContent = message;
                        
                        // Clear after announcement
                        setTimeout(() => {
                            region.textContent = '';
                        }, 1000);
                    }
                };
                
                // Announce form validation errors
                document.addEventListener('invalid', (e) => {
                    const field = e.target;
                    const label = document.querySelector(`label[for="${field.id}"]`);
                    const fieldName = label ? label.textContent : field.name;
                    
                    window.announceToScreenReader(
                        `Błąd walidacji w polu ${fieldName}: ${field.validationMessage}`,
                        'assertive'
                    );
                }, true);
                
                // Announce successful actions
                document.addEventListener('submit', (e) => {
                    const form = e.target;
                    if (form.checkValidity()) {
                        window.announceToScreenReader('Formularz został wysłany');
                    }
                });
            }
        }
        
        // Initialize accessibility manager
        document.addEventListener('DOMContentLoaded', function() {
            window.accessibilityManager = new AccessibilityManager();
        });
        