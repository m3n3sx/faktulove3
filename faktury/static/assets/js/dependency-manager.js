/**
 * Dependency Manager for FaktuLove Application
 * Manages script dependencies and ensures proper loading order
 */

(function() {
    'use strict';

    const DependencyManager = {
        config: {
            checkInterval: 100,
            maxWaitTime: 10000,
            enableLogging: true
        },

        dependencies: {
            'jQuery': {
                check: function() { return typeof $ !== 'undefined' || typeof jQuery !== 'undefined'; },
                fallback: 'jquery-3.7.1.min.js',
                priority: 1
            },
            'Bootstrap': {
                check: function() { return typeof bootstrap !== 'undefined'; },
                depends: ['jQuery'],
                fallback: 'bootstrap.bundle.min.js',
                priority: 2
            },
            'ApexCharts': {
                check: function() { return typeof ApexCharts !== 'undefined'; },
                fallback: 'apexcharts.min.js',
                priority: 3
            },
            'DataTables': {
                check: function() { return typeof $.fn.DataTable !== 'undefined'; },
                depends: ['jQuery'],
                fallback: 'dataTables.min.js',
                priority: 3
            },
            'Flatpickr': {
                check: function() { return typeof flatpickr !== 'undefined'; },
                fallback: 'flatpickr.min.js',
                priority: 3
            },
            'MagnificPopup': {
                check: function() { return typeof $.fn.magnificPopup !== 'undefined'; },
                depends: ['jQuery'],
                fallback: 'magnific-popup.min.js',
                priority: 4
            },
            'Slick': {
                check: function() { return typeof $.fn.slick !== 'undefined'; },
                depends: ['jQuery'],
                fallback: 'slick.min.js',
                priority: 4
            },
            'Toastify': {
                check: function() { return typeof Toastify !== 'undefined'; },
                priority: 2
            }
        },

        waitingCallbacks: {},
        readyDependencies: [],
        failedDependencies: [],
        checkingDependencies: [],

        /**
         * Initialize dependency manager
         */
        init: function() {
            this.startDependencyChecking();
            this.setupEventListeners();
            if (this.config.enableLogging) {
                console.log('DependencyManager initialized');
            }
        },

        /**
         * Start checking for dependencies
         */
        startDependencyChecking: function() {
            const self = this;
            
            // Sort dependencies by priority
            const sortedDeps = Object.keys(this.dependencies).sort(function(a, b) {
                return self.dependencies[a].priority - self.dependencies[b].priority;
            });

            // Check each dependency
            sortedDeps.forEach(function(depName) {
                self.checkDependency(depName);
            });

            // Set up periodic checking
            this.checkInterval = setInterval(function() {
                self.performPeriodicCheck();
            }, this.config.checkInterval);
        },

        /**
         * Check if a specific dependency is available
         */
        checkDependency: function(depName) {
            if (this.readyDependencies.includes(depName) || this.checkingDependencies.includes(depName)) {
                return;
            }

            const dep = this.dependencies[depName];
            if (!dep) {
                console.warn(`Unknown dependency: ${depName}`);
                return;
            }

            this.checkingDependencies.push(depName);

            // Check if dependency's dependencies are ready first
            if (dep.depends) {
                const unreadyDeps = dep.depends.filter(d => !this.readyDependencies.includes(d));
                if (unreadyDeps.length > 0) {
                    // Wait for dependencies first
                    this.waitForDependencies(unreadyDeps, () => {
                        this.performDependencyCheck(depName);
                    });
                    return;
                }
            }

            this.performDependencyCheck(depName);
        },

        /**
         * Perform the actual dependency check
         */
        performDependencyCheck: function(depName) {
            const dep = this.dependencies[depName];
            
            try {
                if (dep.check()) {
                    this.markDependencyReady(depName);
                } else {
                    // Try to load fallback if available
                    if (dep.fallback && window.CDNFallback && typeof window.CDNFallback.loadFallback === 'function') {
                        if (this.config.enableLogging) {
                            console.log(`Loading fallback for ${depName}: ${dep.fallback}`);
                        }
                        try {
                            window.CDNFallback.loadFallback(dep.fallback);
                        } catch (error) {
                            console.warn('CDN fallback failed:', error);
                        }
                    }
                }
            } catch (error) {
                console.error(`Error checking dependency ${depName}:`, error);
                this.markDependencyFailed(depName, error);
            }
        },

        /**
         * Mark dependency as ready
         */
        markDependencyReady: function(depName) {
            if (this.readyDependencies.includes(depName)) return;

            this.readyDependencies.push(depName);
            this.checkingDependencies = this.checkingDependencies.filter(d => d !== depName);

            if (this.config.enableLogging) {
                console.log(`Dependency ready: ${depName}`);
            }

            // Trigger ready event
            this.triggerDependencyEvent('dependencyReady', { name: depName });

            // Execute waiting callbacks
            this.executeWaitingCallbacks(depName);

            // Check if this enables other dependencies
            this.checkDependentLibraries(depName);
        },

        /**
         * Mark dependency as failed
         */
        markDependencyFailed: function(depName, error) {
            this.failedDependencies.push({ name: depName, error: error });
            this.checkingDependencies = this.checkingDependencies.filter(d => d !== depName);

            console.error(`Dependency failed: ${depName}`, error);

            // Trigger failed event
            this.triggerDependencyEvent('dependencyFailed', { name: depName, error: error });

            // Execute waiting callbacks with error
            this.executeWaitingCallbacks(depName, error);
        },

        /**
         * Check libraries that depend on this one
         */
        checkDependentLibraries: function(readyDepName) {
            const self = this;
            
            Object.keys(this.dependencies).forEach(function(depName) {
                const dep = self.dependencies[depName];
                if (dep.depends && dep.depends.includes(readyDepName)) {
                    if (!self.readyDependencies.includes(depName) && !self.checkingDependencies.includes(depName)) {
                        setTimeout(function() {
                            self.checkDependency(depName);
                        }, 100);
                    }
                }
            });
        },

        /**
         * Wait for multiple dependencies
         */
        waitForDependencies: function(depNames, callback) {
            const self = this;
            let readyCount = 0;
            let hasError = false;

            depNames.forEach(function(depName) {
                self.whenReady(depName, function(error) {
                    if (error) {
                        hasError = true;
                        callback(error);
                        return;
                    }
                    
                    readyCount++;
                    if (readyCount === depNames.length && !hasError) {
                        callback();
                    }
                });
            });
        },

        /**
         * Execute callbacks waiting for a specific dependency
         */
        executeWaitingCallbacks: function(depName, error) {
            if (this.waitingCallbacks[depName]) {
                this.waitingCallbacks[depName].forEach(function(callback) {
                    try {
                        callback(error);
                    } catch (e) {
                        console.error(`Error in dependency callback for ${depName}:`, e);
                    }
                });
                delete this.waitingCallbacks[depName];
            }
        },

        /**
         * Perform periodic dependency checking
         */
        performPeriodicCheck: function() {
            const self = this;
            
            // Re-check failed dependencies
            this.failedDependencies.forEach(function(failed) {
                if (self.dependencies[failed.name]) {
                    self.checkDependency(failed.name);
                }
            });

            // Clean up failed list of dependencies that are now ready
            this.failedDependencies = this.failedDependencies.filter(function(failed) {
                return !self.readyDependencies.includes(failed.name);
            });

            // Stop checking if all dependencies are resolved
            const totalDeps = Object.keys(this.dependencies).length;
            const resolvedDeps = this.readyDependencies.length + this.failedDependencies.length;
            
            if (resolvedDeps >= totalDeps) {
                clearInterval(this.checkInterval);
                if (this.config.enableLogging) {
                    console.log('All dependencies resolved, stopping periodic checks');
                }
            }
        },

        /**
         * Setup event listeners for external dependency notifications
         */
        setupEventListeners: function() {
            const self = this;

            // Listen for CDN fallback success events
            window.addEventListener('cdnFallbackFallbackSuccess', function(event) {
                const fallbackUrl = event.detail.fallback;
                
                // Check which dependency this might satisfy
                Object.keys(self.dependencies).forEach(function(depName) {
                    const dep = self.dependencies[depName];
                    if (dep.fallback && fallbackUrl.includes(dep.fallback.replace('.min', ''))) {
                        setTimeout(function() {
                            self.checkDependency(depName);
                        }, 100);
                    }
                });
            });

            // Listen for library-specific ready events
            ['jqueryReady', 'bootstrapReady', 'apexchartsReady', 'datatablesReady'].forEach(function(eventName) {
                window.addEventListener(eventName, function() {
                    const depName = eventName.replace('Ready', '').replace('jquery', 'jQuery').replace('apexcharts', 'ApexCharts').replace('datatables', 'DataTables');
                    if (self.dependencies[depName]) {
                        setTimeout(function() {
                            self.checkDependency(depName);
                        }, 100);
                    }
                });
            });
        },

        /**
         * Public API: Wait for dependency to be ready
         */
        whenReady: function(depName, callback, timeout) {
            if (this.readyDependencies.includes(depName)) {
                callback();
                return;
            }

            const failed = this.failedDependencies.find(f => f.name === depName);
            if (failed) {
                callback(failed.error);
                return;
            }

            // Add to waiting callbacks
            if (!this.waitingCallbacks[depName]) {
                this.waitingCallbacks[depName] = [];
            }
            this.waitingCallbacks[depName].push(callback);

            // Set timeout if specified
            if (timeout) {
                setTimeout(function() {
                    callback(new Error(`Timeout waiting for ${depName}`));
                }, timeout);
            }

            // Start checking this dependency if not already
            if (!this.checkingDependencies.includes(depName)) {
                this.checkDependency(depName);
            }
        },

        /**
         * Public API: Check if dependency is ready
         */
        isReady: function(depName) {
            return this.readyDependencies.includes(depName);
        },

        /**
         * Public API: Check if dependency failed
         */
        hasFailed: function(depName) {
            return this.failedDependencies.some(f => f.name === depName);
        },

        /**
         * Public API: Get dependency status
         */
        getStatus: function(depName) {
            if (this.readyDependencies.includes(depName)) return 'ready';
            if (this.failedDependencies.some(f => f.name === depName)) return 'failed';
            if (this.checkingDependencies.includes(depName)) return 'checking';
            return 'pending';
        },

        /**
         * Public API: Get all dependency statuses
         */
        getAllStatuses: function() {
            const self = this;
            const statuses = {};
            
            Object.keys(this.dependencies).forEach(function(depName) {
                statuses[depName] = self.getStatus(depName);
            });
            
            return statuses;
        },

        /**
         * Public API: Force recheck of dependency
         */
        recheckDependency: function(depName) {
            // Remove from ready and failed lists
            this.readyDependencies = this.readyDependencies.filter(d => d !== depName);
            this.failedDependencies = this.failedDependencies.filter(f => f.name !== depName);
            this.checkingDependencies = this.checkingDependencies.filter(d => d !== depName);
            
            // Recheck
            this.checkDependency(depName);
        },

        /**
         * Public API: Add custom dependency
         */
        addDependency: function(name, config) {
            this.dependencies[name] = {
                check: config.check,
                depends: config.depends || [],
                fallback: config.fallback,
                priority: config.priority || 5
            };
            
            // Start checking immediately
            this.checkDependency(name);
        },

        /**
         * Trigger dependency-related events
         */
        triggerDependencyEvent: function(eventType, data) {
            const event = new CustomEvent('dependencyManager' + eventType.charAt(0).toUpperCase() + eventType.slice(1), {
                detail: data
            });
            window.dispatchEvent(event);
        },

        /**
         * Get statistics about dependencies
         */
        getStats: function() {
            return {
                total: Object.keys(this.dependencies).length,
                ready: this.readyDependencies.length,
                failed: this.failedDependencies.length,
                checking: this.checkingDependencies.length,
                readyList: this.readyDependencies.slice(),
                failedList: this.failedDependencies.slice(),
                checkingList: this.checkingDependencies.slice()
            };
        }
    };

    // Initialize dependency manager when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            DependencyManager.init();
        });
    } else {
        DependencyManager.init();
    }

    // Make DependencyManager globally available
    window.DependencyManager = DependencyManager;

})();