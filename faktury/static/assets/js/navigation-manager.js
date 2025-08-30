
/**
 * Enhanced Navigation Manager for FaktuLove Application
 */

(function() {
    'use strict';

    const NavigationManager = {
        init: function() {
            this.setupEventListeners();
            this.initializeActiveStates();
            this.setupMobileNavigation();
            console.log('✅ NavigationManager initialized');
        },

        setupEventListeners: function() {
            const self = this;

            // Handle all navigation clicks
            $(document).on('click', 'a[href]', function(e) {
                const href = $(this).attr('href');
                
                // Skip external links and javascript: links
                if (!href || href.startsWith('http') || href.startsWith('javascript:') || href === '#') {
                    return;
                }
                
                // Handle OCR navigation
                if (href.includes('ocr')) {
                    console.log('🔗 OCR navigation clicked');
                }
                
                // Update active states
                self.updateActiveState(this);
            });

            // Handle dropdown toggles
            $(document).on('click', '[data-bs-toggle="dropdown"]', function(e) {
                console.log('🔽 Dropdown toggle clicked');
            });

            // Handle mobile menu
            $(document).on('click', '.sidebar-mobile-toggle', function(e) {
                e.preventDefault();
                $('.sidebar').addClass('sidebar-open');
                $('body').addClass('overlay-active');
            });

            $(document).on('click', '.sidebar-close-btn', function(e) {
                e.preventDefault();
                $('.sidebar').removeClass('sidebar-open');
                $('body').removeClass('overlay-active');
            });
        },

        updateActiveState: function(activeLink) {
            // Remove active from all links
            $('.nav-link, .sidebar-menu a').removeClass('active active-page');
            
            // Add active to current link
            $(activeLink).addClass('active active-page');
            $(activeLink).closest('li').addClass('active');
        },

        initializeActiveStates: function() {
            const currentPath = window.location.pathname;
            const self = this;
            
            $('.nav-link, .sidebar-menu a').each(function() {
                const href = $(this).attr('href');
                if (href === currentPath || currentPath.startsWith(href + '/')) {
                    self.updateActiveState(this);
                }
            });
        },

        setupMobileNavigation: function() {
            // Close mobile menu on window resize
            $(window).on('resize', function() {
                if ($(window).width() > 768) {
                    $('.sidebar').removeClass('sidebar-open');
                    $('body').removeClass('overlay-active');
                }
            });
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        NavigationManager.init();
    });

    // Make globally available
    window.NavigationManager = NavigationManager;

})();
