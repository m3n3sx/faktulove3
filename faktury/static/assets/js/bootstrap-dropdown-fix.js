
// Bootstrap Dropdown Fix for FaktuLove
// Ensures dropdown functionality works properly

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Bootstrap Dropdown Fix loading...');
    
    // Wait for Bootstrap to be available
    function initializeDropdowns() {
        if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
            console.log('✅ Bootstrap available, initializing dropdowns');
            
            // Initialize all dropdowns
            const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
            dropdownElements.forEach(function(element) {
                try {
                    new bootstrap.Dropdown(element);
                    console.log('✅ Dropdown initialized:', element);
                } catch (error) {
                    console.error('❌ Dropdown initialization failed:', error);
                }
            });
            
            // Add click handlers for dropdown items
            const dropdownItems = document.querySelectorAll('.dropdown-item');
            dropdownItems.forEach(function(item) {
                item.addEventListener('click', function(e) {
                    const href = this.getAttribute('href');
                    if (href && href !== '' && href !== '#') {
                        console.log('🔗 Navigating to:', href);
                        window.location.href = href;
                    }
                });
            });
            
        } else {
            console.warn('⚠️ Bootstrap not available, retrying in 1 second...');
            setTimeout(initializeDropdowns, 1000);
        }
    }
    
    // Start initialization
    initializeDropdowns();
    
    // Fallback: Manual dropdown handling
    setTimeout(function() {
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
        dropdownToggles.forEach(function(toggle) {
            if (!toggle.hasAttribute('data-dropdown-initialized')) {
                toggle.setAttribute('data-dropdown-initialized', 'true');
                
                toggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const dropdown = this.nextElementSibling;
                    if (dropdown && dropdown.classList.contains('dropdown-menu')) {
                        // Toggle dropdown visibility
                        const isVisible = dropdown.style.display === 'block';
                        
                        // Hide all other dropdowns
                        document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
                            menu.style.display = 'none';
                        });
                        
                        // Toggle current dropdown
                        dropdown.style.display = isVisible ? 'none' : 'block';
                        
                        console.log('🔽 Manual dropdown toggled');
                    }
                });
            }
        });
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
                    menu.style.display = 'none';
                });
            }
        });
        
    }, 2000);
});

// OCR Navigation Fix
function navigateToOCR() {
    console.log('🔗 Navigating to OCR Upload...');
    window.location.href = '/ocr/upload/';
}

// Add OCR navigation to window for global access
window.navigateToOCR = navigateToOCR;

console.log('🎯 Bootstrap Dropdown Fix loaded');
