/**
 * Charts Manager for FaktuLove Application
 * Manages chart initialization, rendering, and fallback handling
 */

(function() {
    'use strict';

    const ChartsManager = {
        config: {
            enableFallback: true,
            retryAttempts: 3,
            retryDelay: 1000,
            enableResponsive: true,
            enableAnimation: true
        },

        charts: {},
        chartElements: [],
        failedCharts: [],
        chartLibraries: {
            ApexCharts: false,
            Chart: false, // Chart.js
            Highcharts: false
        },

        /**
         * Initialize charts manager
         */
        init: function() {
            this.detectChartLibraries();
            this.findChartElements();
            this.setupDependencyListeners();
            this.initializeCharts();
            console.log('ChartsManager initialized');
        },

        /**
         * Detect available chart libraries
         */
        detectChartLibraries: function() {
            this.chartLibraries.ApexCharts = typeof ApexCharts !== 'undefined';
            this.chartLibraries.Chart = typeof Chart !== 'undefined';
            this.chartLibraries.Highcharts = typeof Highcharts !== 'undefined';

            console.log('Available chart libraries:', this.chartLibraries);
        },

        /**
         * Find chart elements in the DOM
         */
        findChartElements: function() {
            // Common chart element selectors
            const selectors = [
                '[data-chart]',
                '.chart',
                '.apex-chart',
                '.apexcharts',
                '#chart',
                '.dashboard-chart',
                '.analytics-chart'
            ];

            const self = this;
            selectors.forEach(function(selector) {
                const elements = document.querySelectorAll(selector);
                elements.forEach(function(element) {
                    if (!self.chartElements.includes(element)) {
                        self.chartElements.push(element);
                    }
                });
            });

            console.log(`Found ${this.chartElements.length} chart elements`);
        },

        /**
         * Setup listeners for dependency availability
         */
        setupDependencyListeners: function() {
            const self = this;

            // Listen for ApexCharts availability
            window.addEventListener('apexchartsReady', function() {
                self.chartLibraries.ApexCharts = true;
                self.initializeApexCharts();
            });

            // Listen for dependency manager events
            window.addEventListener('dependencyManagerDependencyReady', function(event) {
                if (event.detail.name === 'ApexCharts') {
                    self.chartLibraries.ApexCharts = true;
                    self.initializeApexCharts();
                }
            });

            // Periodic check for chart libraries
            const checkInterval = setInterval(function() {
                const wasApexAvailable = self.chartLibraries.ApexCharts;
                self.detectChartLibraries();
                
                if (!wasApexAvailable && self.chartLibraries.ApexCharts) {
                    self.initializeApexCharts();
                }
                
                // Stop checking after 30 seconds
                setTimeout(function() {
                    clearInterval(checkInterval);
                }, 30000);
            }, 1000);
        },

        /**
         * Initialize all charts
         */
        initializeCharts: function() {
            if (this.chartLibraries.ApexCharts) {
                this.initializeApexCharts();
            } else {
                // Try to initialize fallback charts
                this.initializeFallbackCharts();
            }
        },

        /**
         * Initialize ApexCharts
         */
        initializeApexCharts: function() {
            const self = this;
            
            this.chartElements.forEach(function(element) {
                if (element.hasAttribute('data-initialized')) return;
                
                try {
                    self.createApexChart(element);
                } catch (error) {
                    console.error('Failed to create ApexChart:', error);
                    self.handleChartError(element, error);
                }
            });
        },

        /**
         * Create ApexChart instance
         */
        createApexChart: function(element) {
            const chartType = element.getAttribute('data-chart') || 'line';
            const chartId = element.id || 'chart-' + Date.now();
            
            // Get chart configuration
            const config = this.getChartConfig(element, chartType);
            
            // Create chart
            const chart = new ApexCharts(element, config);
            chart.render();
            
            // Store chart reference
            this.charts[chartId] = chart;
            element.setAttribute('data-initialized', 'true');
            element.setAttribute('data-chart-id', chartId);
            
            console.log(`ApexChart created: ${chartId} (${chartType})`);
            
            // Trigger chart created event
            this.triggerChartEvent('chartCreated', {
                id: chartId,
                type: chartType,
                element: element,
                chart: chart
            });
        },

        /**
         * Get chart configuration based on element attributes and type
         */
        getChartConfig: function(element, chartType) {
            const baseConfig = {
                chart: {
                    type: chartType,
                    height: element.getAttribute('data-height') || 350,
                    animations: {
                        enabled: this.config.enableAnimation
                    },
                    toolbar: {
                        show: element.getAttribute('data-toolbar') !== 'false'
                    }
                },
                responsive: this.config.enableResponsive ? [{
                    breakpoint: 768,
                    options: {
                        chart: {
                            height: 250
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }] : [],
                theme: {
                    mode: document.documentElement.getAttribute('data-theme') || 'light'
                }
            };

            // Get data from element attributes or generate sample data
            const data = this.getChartData(element, chartType);
            
            // Merge with chart type specific configuration
            const typeConfig = this.getTypeSpecificConfig(chartType, data);
            
            return this.mergeConfigs(baseConfig, typeConfig);
        },

        /**
         * Get chart data from element or generate sample data
         */
        getChartData: function(element, chartType) {
            // Try to get data from data attribute
            const dataAttr = element.getAttribute('data-chart-data');
            if (dataAttr) {
                try {
                    return JSON.parse(dataAttr);
                } catch (e) {
                    console.warn('Invalid chart data JSON:', e);
                }
            }

            // Generate sample data based on chart type
            return this.generateSampleData(chartType);
        },

        /**
         * Generate sample data for charts
         */
        generateSampleData: function(chartType) {
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
            
            switch (chartType) {
                case 'line':
                case 'area':
                    return {
                        series: [{
                            name: 'Revenue',
                            data: [30, 40, 35, 50, 49, 60]
                        }],
                        categories: months
                    };
                    
                case 'bar':
                case 'column':
                    return {
                        series: [{
                            name: 'Invoices',
                            data: [44, 55, 41, 67, 22, 43]
                        }],
                        categories: months
                    };
                    
                case 'pie':
                case 'donut':
                    return {
                        series: [44, 55, 13, 43, 22],
                        labels: ['Paid', 'Pending', 'Overdue', 'Draft', 'Cancelled']
                    };
                    
                case 'radialBar':
                    return {
                        series: [70],
                        labels: ['Progress']
                    };
                    
                default:
                    return {
                        series: [{
                            name: 'Data',
                            data: [10, 41, 35, 51, 49, 62]
                        }],
                        categories: months
                    };
            }
        },

        /**
         * Get type-specific chart configuration
         */
        getTypeSpecificConfig: function(chartType, data) {
            const config = {
                series: data.series || [],
                xaxis: {
                    categories: data.categories || []
                }
            };

            switch (chartType) {
                case 'pie':
                case 'donut':
                    config.labels = data.labels || [];
                    config.legend = {
                        position: 'bottom'
                    };
                    break;
                    
                case 'radialBar':
                    config.labels = data.labels || [];
                    config.plotOptions = {
                        radialBar: {
                            hollow: {
                                size: '70%'
                            }
                        }
                    };
                    break;
                    
                case 'area':
                    config.fill = {
                        type: 'gradient',
                        gradient: {
                            shadeIntensity: 1,
                            opacityFrom: 0.7,
                            opacityTo: 0.9
                        }
                    };
                    break;
            }

            return config;
        },

        /**
         * Merge chart configurations
         */
        mergeConfigs: function(base, override) {
            const result = JSON.parse(JSON.stringify(base));
            
            for (const key in override) {
                if (override.hasOwnProperty(key)) {
                    if (typeof override[key] === 'object' && !Array.isArray(override[key])) {
                        result[key] = this.mergeConfigs(result[key] || {}, override[key]);
                    } else {
                        result[key] = override[key];
                    }
                }
            }
            
            return result;
        },

        /**
         * Initialize fallback charts when ApexCharts is not available
         */
        initializeFallbackCharts: function() {
            const self = this;
            
            this.chartElements.forEach(function(element) {
                if (element.hasAttribute('data-initialized')) return;
                
                try {
                    self.createFallbackChart(element);
                } catch (error) {
                    console.error('Failed to create fallback chart:', error);
                    self.handleChartError(element, error);
                }
            });
        },

        /**
         * Create fallback chart using HTML/CSS
         */
        createFallbackChart: function(element) {
            const chartType = element.getAttribute('data-chart') || 'line';
            const chartId = element.id || 'fallback-chart-' + Date.now();
            
            // Create simple HTML-based chart
            const fallbackHTML = this.generateFallbackHTML(chartType);
            element.innerHTML = fallbackHTML;
            element.classList.add('fallback-chart', `fallback-${chartType}`);
            element.setAttribute('data-initialized', 'true');
            element.setAttribute('data-fallback', 'true');
            
            console.log(`Fallback chart created: ${chartId} (${chartType})`);
            
            // Add basic styling
            this.addFallbackStyles();
            
            // Trigger chart created event
            this.triggerChartEvent('fallbackChartCreated', {
                id: chartId,
                type: chartType,
                element: element
            });
        },

        /**
         * Generate fallback HTML for charts
         */
        generateFallbackHTML: function(chartType) {
            switch (chartType) {
                case 'bar':
                case 'column':
                    return this.generateFallbackBarChart();
                case 'pie':
                case 'donut':
                    return this.generateFallbackPieChart();
                default:
                    return this.generateFallbackLineChart();
            }
        },

        /**
         * Generate fallback bar chart HTML
         */
        generateFallbackBarChart: function() {
            const data = [65, 45, 80, 30, 55];
            const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May'];
            
            let html = '<div class="fallback-bar-chart">';
            data.forEach(function(value, index) {
                const height = (value / 100) * 200;
                html += `
                    <div class="bar-item">
                        <div class="bar" style="height: ${height}px;" title="${labels[index]}: ${value}%"></div>
                        <div class="bar-label">${labels[index]}</div>
                    </div>
                `;
            });
            html += '</div>';
            html += '<div class="chart-message">Chart library not available. Showing simplified view.</div>';
            
            return html;
        },

        /**
         * Generate fallback pie chart HTML
         */
        generateFallbackPieChart: function() {
            const data = [
                { label: 'Paid', value: 45, color: '#28a745' },
                { label: 'Pending', value: 30, color: '#ffc107' },
                { label: 'Overdue', value: 25, color: '#dc3545' }
            ];
            
            let html = '<div class="fallback-pie-chart">';
            html += '<div class="pie-legend">';
            data.forEach(function(item) {
                html += `
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: ${item.color}"></span>
                        <span class="legend-label">${item.label}: ${item.value}%</span>
                    </div>
                `;
            });
            html += '</div>';
            html += '</div>';
            html += '<div class="chart-message">Chart library not available. Showing data summary.</div>';
            
            return html;
        },

        /**
         * Generate fallback line chart HTML
         */
        generateFallbackLineChart: function() {
            return `
                <div class="fallback-line-chart">
                    <div class="chart-placeholder">
                        <div class="chart-icon">📈</div>
                        <div class="chart-title">Analytics Chart</div>
                        <div class="chart-description">Chart data will be displayed here when the chart library loads.</div>
                    </div>
                </div>
                <div class="chart-message">Loading chart library...</div>
            `;
        },

        /**
         * Add fallback chart styles
         */
        addFallbackStyles: function() {
            if (document.getElementById('fallback-chart-styles')) return;
            
            const styles = `
                <style id="fallback-chart-styles">
                .fallback-chart {
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background: #f9f9f9;
                    text-align: center;
                }
                
                .fallback-bar-chart {
                    display: flex;
                    align-items: end;
                    justify-content: space-around;
                    height: 200px;
                    margin-bottom: 10px;
                }
                
                .bar-item {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                
                .bar {
                    width: 30px;
                    background: #007bff;
                    margin-bottom: 5px;
                    border-radius: 2px 2px 0 0;
                    transition: background-color 0.3s;
                }
                
                .bar:hover {
                    background: #0056b3;
                }
                
                .bar-label {
                    font-size: 12px;
                    color: #666;
                }
                
                .fallback-pie-chart .pie-legend {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                    margin: 20px 0;
                }
                
                .legend-item {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .legend-color {
                    width: 16px;
                    height: 16px;
                    border-radius: 2px;
                }
                
                .chart-placeholder {
                    padding: 40px 20px;
                }
                
                .chart-icon {
                    font-size: 48px;
                    margin-bottom: 10px;
                }
                
                .chart-title {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: #333;
                }
                
                .chart-description {
                    color: #666;
                    font-size: 14px;
                }
                
                .chart-message {
                    font-size: 12px;
                    color: #888;
                    font-style: italic;
                    margin-top: 10px;
                }
                </style>
            `;
            
            document.head.insertAdjacentHTML('beforeend', styles);
        },

        /**
         * Handle chart creation errors
         */
        handleChartError: function(element, error) {
            this.failedCharts.push({
                element: element,
                error: error,
                timestamp: new Date().toISOString()
            });

            // Show error message
            element.innerHTML = `
                <div class="chart-error">
                    <div class="error-icon">⚠️</div>
                    <div class="error-message">Failed to load chart</div>
                    <div class="error-details">${error.message}</div>
                </div>
            `;
            element.classList.add('chart-error-state');

            // Report to error handler
            if (window.ErrorHandler) {
                window.ErrorHandler.reportError(
                    `Chart creation failed: ${error.message}`,
                    'chart',
                    { element: element, error: error }
                );
            }

            this.triggerChartEvent('chartError', {
                element: element,
                error: error
            });
        },

        /**
         * Update chart data
         */
        updateChart: function(chartId, newData) {
            const chart = this.charts[chartId];
            if (chart && chart.updateSeries) {
                chart.updateSeries(newData.series || []);
                
                this.triggerChartEvent('chartUpdated', {
                    id: chartId,
                    data: newData
                });
            }
        },

        /**
         * Destroy chart
         */
        destroyChart: function(chartId) {
            const chart = this.charts[chartId];
            if (chart && chart.destroy) {
                chart.destroy();
                delete this.charts[chartId];
                
                this.triggerChartEvent('chartDestroyed', {
                    id: chartId
                });
            }
        },

        /**
         * Refresh all charts
         */
        refreshCharts: function() {
            // Re-detect libraries
            this.detectChartLibraries();
            
            // Re-initialize charts
            this.chartElements.forEach(function(element) {
                element.removeAttribute('data-initialized');
            });
            
            this.initializeCharts();
        },

        /**
         * Trigger chart events
         */
        triggerChartEvent: function(eventType, data) {
            const event = new CustomEvent('charts' + eventType.charAt(0).toUpperCase() + eventType.slice(1), {
                detail: data
            });
            window.dispatchEvent(event);
        },

        /**
         * Get chart statistics
         */
        getStats: function() {
            return {
                totalCharts: this.chartElements.length,
                initializedCharts: Object.keys(this.charts).length,
                failedCharts: this.failedCharts.length,
                availableLibraries: this.chartLibraries,
                fallbackCharts: this.chartElements.filter(el => el.hasAttribute('data-fallback')).length
            };
        }
    };

    // Initialize charts manager when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            ChartsManager.init();
        });
    } else {
        ChartsManager.init();
    }

    // Make ChartsManager globally available
    window.ChartsManager = ChartsManager;

})();