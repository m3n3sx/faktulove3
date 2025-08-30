/**
 * Application Diagnostics - Tests critical functionality
 * Runs automatic checks and reports issues
 */

class AppDiagnostics {
    constructor() {
        this.issues = [];
        this.checks = [];
    }

    init() {
        console.log('🔍 Starting Application Diagnostics...');
        
        // Run all diagnostic checks
        this.checkJQuery();
        this.checkBootstrap();
        this.checkIconify();
        this.checkDropdowns();
        this.checkStaticFiles();
        this.checkCSRF();
        
        // Report results
        this.reportResults();
    }

    checkJQuery() {
        if (typeof $ === 'undefined' && typeof jQuery === 'undefined') {
            this.addIssue('CRITICAL', 'jQuery not loaded', 'Many features will not work');
        } else {
            this.addCheck('✅ jQuery loaded successfully');
        }
    }

    checkBootstrap() {
        if (typeof bootstrap === 'undefined') {
            this.addIssue('HIGH', 'Bootstrap JS not loaded', 'Dropdowns and modals will not work');
        } else {
            this.addCheck('✅ Bootstrap JS loaded successfully');
        }
    }

    checkIconify() {
        if (typeof Iconify === 'undefined') {
            this.addIssue('HIGH', 'Iconify not loaded', 'Icons will not display');
        } else {
            this.addCheck('✅ Iconify loaded successfully');
        }
    }

    checkDropdowns() {
        const dropdowns = document.querySelectorAll('[data-bs-toggle="dropdown"]');
        if (dropdowns.length > 0) {
            this.addCheck(`✅ Found ${dropdowns.length} dropdown toggles`);
            
            // Test first dropdown
            const firstDropdown = dropdowns[0];
            if (firstDropdown) {
                try {
                    if (typeof bootstrap !== 'undefined') {
                        new bootstrap.Dropdown(firstDropdown);
                        this.addCheck('✅ Dropdown initialization test passed');
                    }
                } catch (error) {
                    this.addIssue('MEDIUM', 'Dropdown initialization failed', error.message);
                }
            }
        } else {
            this.addCheck('ℹ️ No dropdowns found on this page');
        }
    }

    checkStaticFiles() {
        // Check if CSS files are loaded
        const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
        const loadedCSS = Array.from(stylesheets).filter(link => {
            return link.href.includes('remixicon') || 
                   link.href.includes('bootstrap') || 
                   link.href.includes('style.css');
        });
        
        if (loadedCSS.length > 0) {
            this.addCheck(`✅ Found ${loadedCSS.length} critical CSS files`);
        } else {
            this.addIssue('HIGH', 'Critical CSS files missing', 'Styling may be broken');
        }
    }

    checkCSRF() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        
        if (csrfToken || csrfMeta) {
            this.addCheck('✅ CSRF token found');
        } else {
            this.addIssue('MEDIUM', 'CSRF token not found', 'Forms may fail to submit');
        }
    }

    addIssue(severity, title, description) {
        this.issues.push({ severity, title, description });
    }

    addCheck(message) {
        this.checks.push(message);
    }

    reportResults() {
        console.log('\n📊 DIAGNOSTIC RESULTS:');
        console.log('='.repeat(50));
        
        // Report successful checks
        if (this.checks.length > 0) {
            console.log('\n✅ SUCCESSFUL CHECKS:');
            this.checks.forEach(check => console.log(check));
        }
        
        // Report issues
        if (this.issues.length > 0) {
            console.log('\n⚠️ ISSUES FOUND:');
            this.issues.forEach(issue => {
                const icon = issue.severity === 'CRITICAL' ? '🔴' : 
                           issue.severity === 'HIGH' ? '🟠' : '🟡';
                console.log(`${icon} [${issue.severity}] ${issue.title}: ${issue.description}`);
            });
            
            // Show summary
            const critical = this.issues.filter(i => i.severity === 'CRITICAL').length;
            const high = this.issues.filter(i => i.severity === 'HIGH').length;
            const medium = this.issues.filter(i => i.severity === 'MEDIUM').length;
            
            console.log(`\n📈 SUMMARY: ${critical} Critical, ${high} High, ${medium} Medium priority issues`);
            
            if (critical > 0) {
                console.log('🚨 CRITICAL ISSUES DETECTED - Application may not function properly!');
            }
        } else {
            console.log('\n🎉 NO ISSUES FOUND - Application appears to be working correctly!');
        }
        
        console.log('='.repeat(50));
    }

    // Method to test specific functionality
    testDropdownFunctionality() {
        const dropdowns = document.querySelectorAll('[data-bs-toggle="dropdown"]');
        if (dropdowns.length === 0) {
            console.log('❌ No dropdowns to test');
            return;
        }

        console.log(`🧪 Testing ${dropdowns.length} dropdowns...`);
        
        dropdowns.forEach((dropdown, index) => {
            try {
                // Simulate click
                const event = new Event('click', { bubbles: true });
                dropdown.dispatchEvent(event);
                console.log(`✅ Dropdown ${index + 1} click test passed`);
            } catch (error) {
                console.log(`❌ Dropdown ${index + 1} click test failed:`, error.message);
            }
        });
    }

    // Method to test icon rendering
    testIconRendering() {
        const icons = document.querySelectorAll('iconify-icon');
        console.log(`🧪 Testing ${icons.length} icons...`);
        
        let renderedCount = 0;
        icons.forEach((icon, index) => {
            // Check if icon has been rendered (has content)
            if (icon.innerHTML.trim() !== '' || icon.shadowRoot) {
                renderedCount++;
            }
        });
        
        console.log(`✅ ${renderedCount}/${icons.length} icons rendered successfully`);
        
        if (renderedCount < icons.length) {
            console.log('⚠️ Some icons may not be displaying correctly');
        }
    }
}

// Auto-run diagnostics when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const diagnostics = new AppDiagnostics();
    diagnostics.init();
    
    // Make available globally for manual testing
    window.AppDiagnostics = diagnostics;
    
    // Add manual test methods to console
    console.log('💡 Manual test methods available:');
    console.log('- AppDiagnostics.testDropdownFunctionality()');
    console.log('- AppDiagnostics.testIconRendering()');
    
    // Make test methods available globally
    window.testDropdowns = function() { return diagnostics.testDropdownFunctionality(); };
    window.testIcons = function() { return diagnostics.testIconRendering(); };
    
    // Fix DropdownManager access
    if (window.DropdownManager && window.DropdownManager.toggleDropdown) {
        window.testDropdownToggle = function() {
            const dropdown = document.querySelector('[data-bs-toggle="dropdown"]');
            if (dropdown) {
                return window.DropdownManager.toggleDropdown(dropdown);
            } else {
                console.log('No dropdown found to test');
            }
        };
    }
});