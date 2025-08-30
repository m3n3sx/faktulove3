/**
 * Charts Fix - Handles ApexCharts loading issues
 * Provides fallbacks when charts fail to load
 */

// Wait for ApexCharts to load
function waitForApexCharts(callback, maxAttempts = 50) {
    let attempts = 0;
    
    function check() {
        attempts++;
        
        if (typeof ApexCharts !== 'undefined') {
            console.log('✅ ApexCharts loaded successfully');
            callback();
        } else if (attempts < maxAttempts) {
            setTimeout(check, 100);
        } else {
            console.warn('⚠️ ApexCharts failed to load, using fallbacks');
            createChartFallbacks();
        }
    }
    
    check();
}

// Create fallback elements when charts fail
function createChartFallbacks() {
    const chartSelectors = [
        '#widgetChartMonth',
        '#widgetChartQuarter', 
        '#widgetChartYear',
        '#widgetChartWeek',
        '#widgetChartWeekCost',
        '#widgetChartMonthCost',
        '#widgetChartQuarterCost',
        '#widgetChartYearCost'
    ];
    
    chartSelectors.forEach(selector => {
        const element = document.querySelector(selector);
        if (element) {
            element.innerHTML = `
                <div class="d-flex align-items-center justify-content-center h-100 text-muted">
                    <div class="text-center">
                        <i class="ri-bar-chart-line" style="font-size: 2rem;"></i>
                        <div class="mt-2">Wykres ładuje się...</div>
                    </div>
                </div>
            `;
            element.style.minHeight = '200px';
        }
    });
}

// Safe chart creation wrapper
function createChartSafely(selector, options) {
    if (typeof ApexCharts === 'undefined') {
        console.warn(`Cannot create chart for ${selector} - ApexCharts not loaded`);
        return null;
    }
    
    const element = document.querySelector(selector);
    if (!element) {
        console.warn(`Chart element ${selector} not found`);
        return null;
    }
    
    try {
        const chart = new ApexCharts(element, options);
        chart.render();
        return chart;
    } catch (error) {
        console.error(`Failed to create chart for ${selector}:`, error);
        // Create fallback content
        element.innerHTML = `
            <div class="d-flex align-items-center justify-content-center h-100 text-muted">
                <div class="text-center">
                    <i class="ri-bar-chart-line" style="font-size: 2rem;"></i>
                    <div class="mt-2">Wykres niedostępny</div>
                </div>
            </div>
        `;
        element.style.minHeight = '200px';
        return null;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait for ApexCharts and then initialize existing chart functions
    waitForApexCharts(function() {
        // Re-run chart initialization functions if they exist
        if (typeof initializeAnalyticsWidgets === 'function') {
            setTimeout(initializeAnalyticsWidgets, 100);
        }
        
        // Don't auto-run chart functions - they will be called by existing code
        console.log('ApexCharts ready - existing chart functions will handle initialization');
    });
});

// Make available globally
window.createChartSafely = createChartSafely;
window.waitForApexCharts = waitForApexCharts;