/**
 * Error Dashboard for FaktuLove Application
 * Provides a visual dashboard for monitoring errors and system health
 */

(function() {
    'use strict';

    const ErrorDashboard = {
        config: {
            enableDashboard: true,
            enableFloatingWidget: true,
            enableKeyboardShortcut: true,
            keyboardShortcut: 'Ctrl+Shift+E',
            updateInterval: 5000,
            maxDisplayedErrors: 50
        },

        dashboard: null,
        widget: null,
        isVisible: false,
        updateTimer: null,

        /**
         * Initialize error dashboard
         */
        init: function() {
            if (!this.config.enableDashboard) return;

            this.createDashboard();
            this.createFloatingWidget();
            this.setupEventListeners();
            this.startUpdateTimer();
            console.log('ErrorDashboard initialized');
        },

        /**
         * Create main dashboard
         */
        createDashboard: function() {
            this.dashboard = document.createElement('div');
            this.dashboard.id = 'error-dashboard';
            this.dashboard.className = 'error-dashboard';
            this.dashboard.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                z-index: 10000;
                display: none;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            `;

            this.dashboard.innerHTML = this.getDashboardHTML();
            document.body.appendChild(this.dashboard);
        },

        /**
         * Get dashboard HTML structure
         */
        getDashboardHTML: function() {
            return `
                <div class="dashboard-header" style="padding: 20px; border-bottom: 1px solid #333; display: flex; justify-content: between; align-items: center;">
                    <h2 style="margin: 0; color: #ff6b6b;">🚨 Error Dashboard</h2>
                    <div class="dashboard-controls">
                        <button id="clear-errors-btn" style="margin-right: 10px; padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 3px; cursor: pointer;">Clear All</button>
                        <button id="export-errors-btn" style="margin-right: 10px; padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer;">Export</button>
                        <button id="close-dashboard-btn" style="padding: 5px 10px; background: #6c757d; color: white; border: none; border-radius: 3px; cursor: pointer;">Close</button>
                    </div>
                </div>
                <div class="dashboard-content" style="padding: 20px;">
                    <div class="dashboard-stats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
                        <div class="stat-card" style="background: #333; padding: 15px; border-radius: 5px;">
                            <h4 style="margin: 0 0 10px 0; color: #ff6b6b;">JavaScript Errors</h4>
                            <div id="js-error-count" style="font-size: 24px; font-weight: bold;">0</div>
                        </div>
                        <div class="stat-card" style="background: #333; padding: 15px; border-radius: 5px;">
                            <h4 style="margin: 0 0 10px 0; color: #ffc107;">Asset Errors</h4>
                            <div id="asset-error-count" style="font-size: 24px; font-weight: bold;">0</div>
                        </div>
                        <div class="stat-card" style="background: #333; padding: 15px; border-radius: 5px;">
                            <h4 style="margin: 0 0 10px 0; color: #17a2b8;">Network Errors</h4>
                            <div id="network-error-count" style="font-size: 24px; font-weight: bold;">0</div>
                        </div>
                        <div class="stat-card" style="background: #333; padding: 15px; border-radius: 5px;">
                            <h4 style="margin: 0 0 10px 0; color: #28a745;">System Health</h4>
                            <div id="system-health" style="font-size: 24px; font-weight: bold;">Good</div>
                        </div>
                    </div>
                    
                    <div class="dashboard-tabs" style="margin-bottom: 20px;">
                        <button class="tab-btn active" data-tab="recent" style="padding: 10px 20px; background: #007bff; color: white; border: none; margin-right: 5px; cursor: pointer;">Recent Errors</button>
                        <button class="tab-btn" data-tab="assets" style="padding: 10px 20px; background: #333; color: white; border: none; margin-right: 5px; cursor: pointer;">Asset Errors</button>
                        <button class="tab-btn" data-tab="performance" style="padding: 10px 20px; background: #333; color: white; border: none; margin-right: 5px; cursor: pointer;">Performance</button>
                        <button class="tab-btn" data-tab="dependencies" style="padding: 10px 20px; background: #333; color: white; border: none; cursor: pointer;">Dependencies</button>
                    </div>
                    
                    <div class="dashboard-panels">
                        <div id="recent-panel" class="panel active" style="display: block;">
                            <div id="recent-errors" style="background: #222; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto;"></div>
                        </div>
                        <div id="assets-panel" class="panel" style="display: none;">
                            <div id="asset-errors" style="background: #222; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto;"></div>
                        </div>
                        <div id="performance-panel" class="panel" style="display: none;">
                            <div id="performance-data" style="background: #222; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto;"></div>
                        </div>
                        <div id="dependencies-panel" class="panel" style="display: none;">
                            <div id="dependencies-data" style="background: #222; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto;"></div>
                        </div>
                    </div>
                </div>
            `;
        },

        /**
         * Create floating widget
         */
        createFloatingWidget: function() {
            if (!this.config.enableFloatingWidget) return;

            this.widget = document.createElement('div');
            this.widget.id = 'error-widget';
            this.widget.className = 'error-widget';
            this.widget.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 60px;
                height: 60px;
                background: #dc3545;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 24px;
                cursor: pointer;
                z-index: 9999;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                transition: all 0.3s ease;
                opacity: 0.8;
            `;

            this.widget.innerHTML = '🚨';
            this.widget.title = 'Click to open Error Dashboard (Ctrl+Shift+E)';

            // Initially hidden
            this.widget.style.display = 'none';

            document.body.appendChild(this.widget);
        },

        /**
         * Setup event listeners
         */
        setupEventListeners: function() {
            const self = this;

            // Widget click
            if (this.widget) {
                this.widget.addEventListener('click', function() {
                    self.toggleDashboard();
                });

                // Widget hover effects
                this.widget.addEventListener('mouseenter', function() {
                    this.style.opacity = '1';
                    this.style.transform = 'scale(1.1)';
                });

                this.widget.addEventListener('mouseleave', function() {
                    this.style.opacity = '0.8';
                    this.style.transform = 'scale(1)';
                });
            }

            // Dashboard controls
            if (this.dashboard) {
                this.dashboard.addEventListener('click', function(e) {
                    if (e.target.id === 'close-dashboard-btn') {
                        self.hideDashboard();
                    } else if (e.target.id === 'clear-errors-btn') {
                        self.clearAllErrors();
                    } else if (e.target.id === 'export-errors-btn') {
                        self.exportErrors();
                    } else if (e.target.classList.contains('tab-btn')) {
                        self.switchTab(e.target.dataset.tab);
                    }
                });

                // Close on escape key
                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Escape' && self.isVisible) {
                        self.hideDashboard();
                    }
                });
            }

            // Keyboard shortcut
            if (this.config.enableKeyboardShortcut) {
                document.addEventListener('keydown', function(e) {
                    if (e.ctrlKey && e.shiftKey && e.key === 'E') {
                        e.preventDefault();
                        self.toggleDashboard();
                    }
                });
            }

            // Listen for error events
            window.addEventListener('errorHandlerError', function(e) {
                self.updateErrorCounts();
                self.updateWidget();
            });

            window.addEventListener('assetMonitorAssetFailed', function(e) {
                self.updateErrorCounts();
                self.updateWidget();
            });

            window.addEventListener('assetLoadingMonitorAssetError', function(e) {
                self.updateErrorCounts();
                self.updateWidget();
            });
        },

        /**
         * Start update timer
         */
        startUpdateTimer: function() {
            const self = this;
            
            this.updateTimer = setInterval(function() {
                if (self.isVisible) {
                    self.updateDashboard();
                }
                self.updateWidget();
            }, this.config.updateInterval);
        },

        /**
         * Toggle dashboard visibility
         */
        toggleDashboard: function() {
            if (this.isVisible) {
                this.hideDashboard();
            } else {
                this.showDashboard();
            }
        },

        /**
         * Show dashboard
         */
        showDashboard: function() {
            if (!this.dashboard) return;

            this.dashboard.style.display = 'block';
            this.isVisible = true;
            this.updateDashboard();
            
            // Animate in
            this.dashboard.style.opacity = '0';
            setTimeout(() => {
                this.dashboard.style.opacity = '1';
            }, 10);
        },

        /**
         * Hide dashboard
         */
        hideDashboard: function() {
            if (!this.dashboard) return;

            this.dashboard.style.display = 'none';
            this.isVisible = false;
        },

        /**
         * Update dashboard content
         */
        updateDashboard: function() {
            this.updateErrorCounts();
            this.updateRecentErrors();
            this.updateAssetErrors();
            this.updatePerformanceData();
            this.updateDependenciesData();
            this.updateSystemHealth();
        },

        /**
         * Update error counts
         */
        updateErrorCounts: function() {
            const jsErrorCount = this.getJavaScriptErrorCount();
            const assetErrorCount = this.getAssetErrorCount();
            const networkErrorCount = this.getNetworkErrorCount();

            const jsCountEl = document.getElementById('js-error-count');
            const assetCountEl = document.getElementById('asset-error-count');
            const networkCountEl = document.getElementById('network-error-count');

            if (jsCountEl) jsCountEl.textContent = jsErrorCount;
            if (assetCountEl) assetCountEl.textContent = assetErrorCount;
            if (networkCountEl) networkCountEl.textContent = networkErrorCount;
        },

        /**
         * Update recent errors panel
         */
        updateRecentErrors: function() {
            const recentErrorsEl = document.getElementById('recent-errors');
            if (!recentErrorsEl) return;

            const errors = this.getAllRecentErrors();
            
            if (errors.length === 0) {
                recentErrorsEl.innerHTML = '<p style="color: #28a745;">No recent errors 🎉</p>';
                return;
            }

            let html = '';
            errors.slice(0, this.config.maxDisplayedErrors).forEach(error => {
                html += this.formatErrorHTML(error);
            });

            recentErrorsEl.innerHTML = html;
        },

        /**
         * Update asset errors panel
         */
        updateAssetErrors: function() {
            const assetErrorsEl = document.getElementById('asset-errors');
            if (!assetErrorsEl) return;

            const assetErrors = this.getAssetErrors();
            
            if (assetErrors.length === 0) {
                assetErrorsEl.innerHTML = '<p style="color: #28a745;">No asset errors 🎉</p>';
                return;
            }

            let html = '<h5>Failed Assets:</h5>';
            assetErrors.forEach(error => {
                html += `
                    <div style="margin-bottom: 10px; padding: 10px; background: #333; border-radius: 3px;">
                        <div style="color: #ffc107; font-weight: bold;">${error.src}</div>
                        <div style="color: #ccc; font-size: 12px;">Type: ${error.type} | Time: ${error.timestamp}</div>
                    </div>
                `;
            });

            assetErrorsEl.innerHTML = html;
        },

        /**
         * Update performance data panel
         */
        updatePerformanceData: function() {
            const performanceEl = document.getElementById('performance-data');
            if (!performanceEl) return;

            const performanceData = this.getPerformanceData();
            
            let html = '<h5>Performance Metrics:</h5>';
            
            if (performanceData.navigation) {
                html += `
                    <div style="margin-bottom: 15px; padding: 10px; background: #333; border-radius: 3px;">
                        <h6 style="color: #17a2b8; margin: 0 0 10px 0;">Page Load Performance</h6>
                        <div>DOM Content Loaded: ${performanceData.navigation.domContentLoaded.toFixed(2)}ms</div>
                        <div>Load Complete: ${performanceData.navigation.loadComplete.toFixed(2)}ms</div>
                        <div>Server Response: ${performanceData.navigation.serverResponse.toFixed(2)}ms</div>
                    </div>
                `;
            }

            if (performanceData.resources) {
                html += `
                    <div style="margin-bottom: 15px; padding: 10px; background: #333; border-radius: 3px;">
                        <h6 style="color: #17a2b8; margin: 0 0 10px 0;">Resource Loading</h6>
                        <div>Total Resources: ${performanceData.resources.count}</div>
                        <div>Average Load Time: ${performanceData.resources.averageLoadTime.toFixed(2)}ms</div>
                        <div>Slow Resources: ${performanceData.resources.slowCount}</div>
                    </div>
                `;
            }

            performanceEl.innerHTML = html;
        },

        /**
         * Update dependencies data panel
         */
        updateDependenciesData: function() {
            const dependenciesEl = document.getElementById('dependencies-data');
            if (!dependenciesEl) return;

            const dependenciesData = this.getDependenciesData();
            
            let html = '<h5>Dependency Status:</h5>';
            
            Object.entries(dependenciesData).forEach(([name, status]) => {
                const statusColor = status === 'ready' ? '#28a745' : 
                                  status === 'failed' ? '#dc3545' : '#ffc107';
                
                html += `
                    <div style="margin-bottom: 10px; padding: 10px; background: #333; border-radius: 3px; display: flex; justify-content: space-between;">
                        <span>${name}</span>
                        <span style="color: ${statusColor}; font-weight: bold;">${status.toUpperCase()}</span>
                    </div>
                `;
            });

            dependenciesEl.innerHTML = html;
        },

        /**
         * Update system health indicator
         */
        updateSystemHealth: function() {
            const healthEl = document.getElementById('system-health');
            if (!healthEl) return;

            const health = this.calculateSystemHealth();
            
            healthEl.textContent = health.status;
            healthEl.style.color = health.color;
        },

        /**
         * Update floating widget
         */
        updateWidget: function() {
            if (!this.widget) return;

            const totalErrors = this.getTotalErrorCount();
            
            if (totalErrors > 0) {
                this.widget.style.display = 'flex';
                this.widget.innerHTML = totalErrors > 99 ? '99+' : totalErrors.toString();
                
                // Pulse animation for new errors
                this.widget.style.animation = 'pulse 1s ease-in-out';
                setTimeout(() => {
                    this.widget.style.animation = '';
                }, 1000);
            } else {
                this.widget.style.display = 'none';
            }
        },

        /**
         * Switch dashboard tabs
         */
        switchTab: function(tabName) {
            // Update tab buttons
            const tabBtns = this.dashboard.querySelectorAll('.tab-btn');
            tabBtns.forEach(btn => {
                btn.classList.remove('active');
                btn.style.background = '#333';
            });

            const activeBtn = this.dashboard.querySelector(`[data-tab="${tabName}"]`);
            if (activeBtn) {
                activeBtn.classList.add('active');
                activeBtn.style.background = '#007bff';
            }

            // Update panels
            const panels = this.dashboard.querySelectorAll('.panel');
            panels.forEach(panel => {
                panel.style.display = 'none';
            });

            const activePanel = document.getElementById(`${tabName}-panel`);
            if (activePanel) {
                activePanel.style.display = 'block';
            }
        },

        /**
         * Clear all errors
         */
        clearAllErrors: function() {
            if (window.ErrorHandler) {
                window.ErrorHandler.clearErrors();
            }
            
            if (window.AssetMonitor) {
                window.AssetMonitor.assets.failed = [];
            }
            
            if (window.AssetLoadingMonitor) {
                window.AssetLoadingMonitor.errors = {
                    notFound: [],
                    networkErrors: [],
                    timeouts: []
                };
            }

            this.updateDashboard();
            this.updateWidget();
        },

        /**
         * Export errors to file
         */
        exportErrors: function() {
            const errors = {
                timestamp: new Date().toISOString(),
                javascript: this.getJavaScriptErrors(),
                assets: this.getAssetErrors(),
                network: this.getNetworkErrors(),
                performance: this.getPerformanceData(),
                dependencies: this.getDependenciesData()
            };

            const blob = new Blob([JSON.stringify(errors, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `error-report-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        },

        /**
         * Format error for display
         */
        formatErrorHTML: function(error) {
            const timeAgo = this.getTimeAgo(error.timestamp);
            const typeColor = this.getErrorTypeColor(error.type);
            
            return `
                <div style="margin-bottom: 15px; padding: 10px; background: #333; border-radius: 3px; border-left: 4px solid ${typeColor};">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span style="color: ${typeColor}; font-weight: bold;">${error.type.toUpperCase()}</span>
                        <span style="color: #999; font-size: 12px;">${timeAgo}</span>
                    </div>
                    <div style="color: #fff; margin-bottom: 5px;">${error.message}</div>
                    ${error.filename ? `<div style="color: #ccc; font-size: 12px;">File: ${error.filename}:${error.lineno}</div>` : ''}
                    ${error.stack ? `<details style="margin-top: 10px;"><summary style="color: #17a2b8; cursor: pointer;">Stack Trace</summary><pre style="color: #ccc; font-size: 11px; margin: 5px 0 0 0; white-space: pre-wrap;">${error.stack}</pre></details>` : ''}
                </div>
            `;
        },

        /**
         * Data collection methods
         */
        getAllRecentErrors: function() {
            const errors = [];
            
            if (window.ErrorHandler) {
                errors.push(...window.ErrorHandler.errors);
            }
            
            if (window.AssetLoadingMonitor) {
                errors.push(...window.AssetLoadingMonitor.errors.notFound);
                errors.push(...window.AssetLoadingMonitor.errors.networkErrors);
                errors.push(...window.AssetLoadingMonitor.errors.timeouts);
            }

            return errors.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        },

        getJavaScriptErrors: function() {
            return window.ErrorHandler ? window.ErrorHandler.errors.filter(e => e.type === 'javascript') : [];
        },

        getAssetErrors: function() {
            const errors = [];
            
            if (window.AssetMonitor) {
                errors.push(...window.AssetMonitor.assets.failed);
            }
            
            if (window.AssetLoadingMonitor) {
                errors.push(...window.AssetLoadingMonitor.errors.notFound);
            }

            return errors;
        },

        getNetworkErrors: function() {
            return window.AssetLoadingMonitor ? window.AssetLoadingMonitor.errors.networkErrors : [];
        },

        getPerformanceData: function() {
            const data = {};
            
            if (window.AssetMonitor && window.AssetMonitor.lastPerformanceReport) {
                data.resources = {
                    count: window.AssetMonitor.lastPerformanceReport.totalAssets,
                    averageLoadTime: window.AssetMonitor.lastPerformanceReport.totalLoadTime / window.AssetMonitor.lastPerformanceReport.totalAssets,
                    slowCount: Object.values(window.AssetMonitor.performance.loadTimes).filter(t => t > 5000).length
                };
            }
            
            if (window.AssetLoadingMonitor && window.AssetLoadingMonitor.performance.navigation) {
                data.navigation = window.AssetLoadingMonitor.performance.navigation;
            }

            return data;
        },

        getDependenciesData: function() {
            return window.DependencyManager ? window.DependencyManager.getAllStatuses() : {};
        },

        /**
         * Count methods
         */
        getJavaScriptErrorCount: function() {
            return this.getJavaScriptErrors().length;
        },

        getAssetErrorCount: function() {
            return this.getAssetErrors().length;
        },

        getNetworkErrorCount: function() {
            return this.getNetworkErrors().length;
        },

        getTotalErrorCount: function() {
            return this.getJavaScriptErrorCount() + this.getAssetErrorCount() + this.getNetworkErrorCount();
        },

        /**
         * Calculate system health
         */
        calculateSystemHealth: function() {
            const totalErrors = this.getTotalErrorCount();
            const criticalErrors = this.getJavaScriptErrorCount();
            
            if (criticalErrors > 5 || totalErrors > 20) {
                return { status: 'Critical', color: '#dc3545' };
            } else if (criticalErrors > 2 || totalErrors > 10) {
                return { status: 'Warning', color: '#ffc107' };
            } else if (totalErrors > 0) {
                return { status: 'Minor Issues', color: '#17a2b8' };
            } else {
                return { status: 'Good', color: '#28a745' };
            }
        },

        /**
         * Utility methods
         */
        getTimeAgo: function(timestamp) {
            const now = new Date();
            const time = new Date(timestamp);
            const diff = now - time;
            
            if (diff < 60000) return 'Just now';
            if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
            if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
            return Math.floor(diff / 86400000) + 'd ago';
        },

        getErrorTypeColor: function(type) {
            switch (type) {
                case 'javascript': return '#dc3545';
                case 'resource': return '#ffc107';
                case 'network': return '#17a2b8';
                case 'promise': return '#6f42c1';
                default: return '#6c757d';
            }
        }
    };

    // Initialize error dashboard when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            ErrorDashboard.init();
        });
    } else {
        ErrorDashboard.init();
    }

    // Make ErrorDashboard globally available
    window.ErrorDashboard = ErrorDashboard;

})();