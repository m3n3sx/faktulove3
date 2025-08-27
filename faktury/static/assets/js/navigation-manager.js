/**
 * Navigation Manager for FaktuLove Application
 * Manages navigation functionality, menus, and routing
 */

(function() {
    'use strict';

    const NavigationManager = {
        config: {
            enableSmoothScrolling: true,
            enableActiveStateTracking: true,
            enableMobileMenu: true,
            enableBreadcrumbs: true
        },

        elements: {
            sidebar: null,
            mobileToggle: null,
            navLinks: [],
            breadcrumbs: null
        },

        state: {
            sidebarOpen: false,
            currentPage: '',
            navigationHistory: []
        },

        /**
         * Initialize navigation manager
         */
        init: function() {
            this.findNavigationElements();
            this.setupEventListeners();
            this.initializeActiveStates();
            this.setupMobileNavigation();
            this.initializeBreadcrumbs();
            console.log('NavigationManager initialized');
        },

        /**
         * Find navigation elements in the DOM
         */
        findNavigationElements: function() {
            // Find sidebar
            this.elements.sidebar = document.querySelector('.sidebar, .navigation-sidebar, #sidebar');
            
            // Find mobile toggle
            this.elements.mobileToggle = document.querySelector('.mobile-menu-toggle, .navbar-toggler, .menu-toggle');
            
            // Find navigation links
            this.elements.navLinks = Array.from(document.querySelectorAll('.nav-link, .sidebar-link, .navigation-link'));
            
            // Find breadcrumbs
            this.elements.breadcrumbs = document.querySelector('.breadcrumb, .breadcrumbs');
            
            if (this.elements.navLinks.length === 0) {
                // Fallback: find any links in navigation areas
                const navAreas = document.querySelectorAll('nav, .sidebar, .navigation');
                navAreas.forEach(area => {
                    const links = area.querySelectorAll('a');
                    this.elements.navLinks.push(...links);
                });
            }
        },

        /**
         * Setup event listeners for navigation
         */
        setupEventListeners: function() {
            const self = this;

            // Mobile menu toggle
            if (this.elements.mobileToggle) {
                this.elements.mobileToggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    self.toggleMobileMenu();
                });
            }

            // Navigation link clicks
            this.elements.navLinks.forEach(function(link) {
                link.addEventListener('click', function(e) {
                    self.handleNavigationClick(e, this);
                });
            });

            // Handle browser back/forward
            window.addEventListener('popstate', function(e) {
                self.handlePopState(e);
            });

            // Close mobile menu on outside click
            document.addEventListener('click', function(e) {
                if (self.state.sidebarOpen && !self.isClickInsideNavigation(e)) {
                    self.closeMobileMenu();
                }
            });

            // Handle escape key for mobile menu
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && self.state.sidebarOpen) {
                    self.closeMobileMenu();
                }
            });
        },

        /**
         * Handle navigation link clicks
         */
        handleNavigationClick: function(event, linkElement) {
            const href = linkElement.getAttribute('href');
            
            // Skip external links and anchors
            if (!href || href.startsWith('http') || href.startsWith('mailto:') || href.startsWith('tel:')) {
                return;
            }

            // Handle anchor links
            if (href.startsWith('#')) {
                event.preventDefault();
                this.scrollToAnchor(href.substring(1));
                return;
            }

            // Update active state
            this.updateActiveState(linkElement);
            
            // Add to navigation history
            this.addToHistory(href, linkElement.textContent.trim());

            // Close mobile menu if open
            if (this.state.sidebarOpen) {
                this.closeMobileMenu();
            }

            // Trigger navigation event
            this.triggerNavigationEvent('navigationClick', {
                href: href,
                text: linkElement.textContent.trim(),
                element: linkElement
            });
        },

        /**
         * Update active navigation state
         */
        updateActiveState: function(activeLink) {
            if (!this.config.enableActiveStateTracking) return;

            // Remove active class from all links
            this.elements.navLinks.forEach(function(link) {
                link.classList.remove('active', 'current');
                const parent = link.closest('li');
                if (parent) {
                    parent.classList.remove('active', 'current');
                }
            });

            // Add active class to current link
            activeLink.classList.add('active');
            const parentLi = activeLink.closest('li');
            if (parentLi) {
                parentLi.classList.add('active');
            }

            // Handle nested menus
            this.updateNestedMenuState(activeLink);
        },

        /**
         * Initialize active states based on current URL
         */
        initializeActiveStates: function() {
            const currentPath = window.location.pathname;
            const self = this;

            this.elements.navLinks.forEach(function(link) {
                const href = link.getAttribute('href');
                if (href && (href === currentPath || currentPath.startsWith(href + '/'))) {
                    self.updateActiveState(link);
                }
            });
        },

        /**
         * Update nested menu states
         */
        updateNestedMenuState: function(activeLink) {
            // Find parent menu items
            let parent = activeLink.closest('ul');
            while (parent) {
                const parentLi = parent.closest('li');
                if (parentLi) {
                    parentLi.classList.add('has-active-child');
                    
                    // Expand parent menu if collapsed
                    const submenu = parentLi.querySelector('ul');
                    if (submenu) {
                        submenu.classList.add('show', 'expanded');
                    }
                }
                parent = parent.parentElement ? parent.parentElement.closest('ul') : null;
            }
        },

        /**
         * Toggle mobile menu
         */
        toggleMobileMenu: function() {
            if (this.state.sidebarOpen) {
                this.closeMobileMenu();
            } else {
                this.openMobileMenu();
            }
        },

        /**
         * Open mobile menu
         */
        openMobileMenu: function() {
            if (!this.config.enableMobileMenu) return;

            this.state.sidebarOpen = true;
            
            if (this.elements.sidebar) {
                this.elements.sidebar.classList.add('open', 'show');
            }
            
            if (this.elements.mobileToggle) {
                this.elements.mobileToggle.classList.add('active');
            }

            // Add body class to prevent scrolling
            document.body.classList.add('mobile-menu-open');

            this.triggerNavigationEvent('mobileMenuOpen');
        },

        /**
         * Close mobile menu
         */
        closeMobileMenu: function() {
            this.state.sidebarOpen = false;
            
            if (this.elements.sidebar) {
                this.elements.sidebar.classList.remove('open', 'show');
            }
            
            if (this.elements.mobileToggle) {
                this.elements.mobileToggle.classList.remove('active');
            }

            // Remove body class
            document.body.classList.remove('mobile-menu-open');

            this.triggerNavigationEvent('mobileMenuClose');
        },

        /**
         * Setup mobile navigation
         */
        setupMobileNavigation: function() {
            if (!this.config.enableMobileMenu) return;

            // Create mobile toggle if it doesn't exist
            if (!this.elements.mobileToggle && this.elements.sidebar) {
                this.createMobileToggle();
            }

            // Handle window resize
            const self = this;
            window.addEventListener('resize', function() {
                if (window.innerWidth > 768 && self.state.sidebarOpen) {
                    self.closeMobileMenu();
                }
            });
        },

        /**
         * Create mobile toggle button
         */
        createMobileToggle: function() {
            const toggle = document.createElement('button');
            toggle.className = 'mobile-menu-toggle';
            toggle.innerHTML = '<span></span><span></span><span></span>';
            toggle.setAttribute('aria-label', 'Toggle navigation menu');
            
            // Insert at the beginning of the page
            const header = document.querySelector('header, .header, .navbar');
            if (header) {
                header.insertBefore(toggle, header.firstChild);
            } else {
                document.body.insertBefore(toggle, document.body.firstChild);
            }
            
            this.elements.mobileToggle = toggle;
        },

        /**
         * Check if click is inside navigation
         */
        isClickInsideNavigation: function(event) {
            return this.elements.sidebar && (
                this.elements.sidebar.contains(event.target) ||
                (this.elements.mobileToggle && this.elements.mobileToggle.contains(event.target))
            );
        },

        /**
         * Scroll to anchor element
         */
        scrollToAnchor: function(anchorId) {
            const target = document.getElementById(anchorId);
            if (target) {
                if (this.config.enableSmoothScrolling) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                } else {
                    target.scrollIntoView();
                }
                
                this.triggerNavigationEvent('anchorScroll', { anchorId: anchorId, target: target });
            }
        },

        /**
         * Handle browser back/forward navigation
         */
        handlePopState: function(event) {
            // Update active states based on new URL
            this.initializeActiveStates();
            
            this.triggerNavigationEvent('popState', { state: event.state });
        },

        /**
         * Add to navigation history
         */
        addToHistory: function(href, title) {
            this.state.navigationHistory.push({
                href: href,
                title: title,
                timestamp: new Date().toISOString()
            });

            // Keep only last 50 entries
            if (this.state.navigationHistory.length > 50) {
                this.state.navigationHistory = this.state.navigationHistory.slice(-50);
            }
        },

        /**
         * Initialize breadcrumbs
         */
        initializeBreadcrumbs: function() {
            if (!this.config.enableBreadcrumbs || !this.elements.breadcrumbs) return;

            this.updateBreadcrumbs();
        },

        /**
         * Update breadcrumbs based on current path
         */
        updateBreadcrumbs: function() {
            if (!this.elements.breadcrumbs) return;

            const path = window.location.pathname;
            const segments = path.split('/').filter(segment => segment);
            
            let breadcrumbHTML = '<li class="breadcrumb-item"><a href="/">Home</a></li>';
            let currentPath = '';

            segments.forEach(function(segment, index) {
                currentPath += '/' + segment;
                const isLast = index === segments.length - 1;
                const title = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
                
                if (isLast) {
                    breadcrumbHTML += `<li class="breadcrumb-item active">${title}</li>`;
                } else {
                    breadcrumbHTML += `<li class="breadcrumb-item"><a href="${currentPath}">${title}</a></li>`;
                }
            });

            this.elements.breadcrumbs.innerHTML = breadcrumbHTML;
        },

        /**
         * Highlight navigation item by URL
         */
        highlightNavigation: function(url) {
            const matchingLink = this.elements.navLinks.find(function(link) {
                return link.getAttribute('href') === url;
            });

            if (matchingLink) {
                this.updateActiveState(matchingLink);
            }
        },

        /**
         * Get current navigation state
         */
        getCurrentState: function() {
            return {
                sidebarOpen: this.state.sidebarOpen,
                currentPage: window.location.pathname,
                activeLinks: this.elements.navLinks.filter(link => link.classList.contains('active')),
                navigationHistory: this.state.navigationHistory.slice(-10)
            };
        },

        /**
         * Trigger navigation events
         */
        triggerNavigationEvent: function(eventType, data) {
            const event = new CustomEvent('navigation' + eventType.charAt(0).toUpperCase() + eventType.slice(1), {
                detail: data || {}
            });
            window.dispatchEvent(event);
        },

        /**
         * Public API: Navigate to URL
         */
        navigateTo: function(url, title) {
            if (title) {
                history.pushState({}, title, url);
            } else {
                window.location.href = url;
            }
            
            this.addToHistory(url, title || url);
            this.highlightNavigation(url);
        },

        /**
         * Public API: Add navigation item
         */
        addNavigationItem: function(href, text, parentSelector) {
            const link = document.createElement('a');
            link.href = href;
            link.textContent = text;
            link.className = 'nav-link';
            
            const li = document.createElement('li');
            li.appendChild(link);
            
            const parent = parentSelector ? document.querySelector(parentSelector) : this.elements.sidebar;
            if (parent) {
                parent.appendChild(li);
                this.elements.navLinks.push(link);
                
                // Add event listener
                const self = this;
                link.addEventListener('click', function(e) {
                    self.handleNavigationClick(e, this);
                });
            }
        },

        /**
         * Public API: Remove navigation item
         */
        removeNavigationItem: function(href) {
            const linkIndex = this.elements.navLinks.findIndex(link => link.getAttribute('href') === href);
            if (linkIndex !== -1) {
                const link = this.elements.navLinks[linkIndex];
                const li = link.closest('li');
                if (li) {
                    li.remove();
                }
                this.elements.navLinks.splice(linkIndex, 1);
            }
        }
    };

    // Initialize navigation manager when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            NavigationManager.init();
        });
    } else {
        NavigationManager.init();
    }

    // Make NavigationManager globally available
    window.NavigationManager = NavigationManager;

})();