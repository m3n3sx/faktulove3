/**
 * Page Manager for FaktuLove Application
 * Manages page-specific functionality and initialization
 */

(function() {
    'use strict';

    const PageManager = {
        config: {
            enablePageTransitions: true,
            enableLazyLoading: true,
            enableProgressBar: true,
            transitionDuration: 300
        },

        currentPage: '',
        pageModules: {},
        loadedModules: [],
        pageData: {},

        /**
         * Initialize page manager
         */
        init: function() {
            this.detectCurrentPage();
            this.setupPageModules();
            this.initializeCurrentPage();
            this.setupEventListeners();
            console.log('PageManager initialized for page:', this.currentPage);
        },

        /**
         * Detect current page from URL or body class
         */
        detectCurrentPage: function() {
            // Try to get page from body class
            const bodyClasses = document.body.className.split(' ');
            const pageClass = bodyClasses.find(cls => cls.startsWith('page-'));
            
            if (pageClass) {
                this.currentPage = pageClass.replace('page-', '');
                return;
            }

            // Try to get page from URL path
            const path = window.location.pathname;
            const segments = path.split('/').filter(segment => segment);
            
            if (segments.length > 0) {
                this.currentPage = segments[0];
            } else {
                this.currentPage = 'dashboard';
            }

            // Add page class to body
            document.body.classList.add(`page-${this.currentPage}`);
        },

        /**
         * Setup page-specific modules
         */
        setupPageModules: function() {
            this.pageModules = {
                'dashboard': {
                    init: this.initDashboardPage.bind(this),
                    dependencies: ['ChartsManager'],
                    scripts: []
                },
                'faktury': {
                    init: this.initInvoicesPage.bind(this),
                    dependencies: ['TablesManager', 'InvoiceFormManager'],
                    scripts: []
                },
                'kontrahenci': {
                    init: this.initContractorsPage.bind(this),
                    dependencies: ['TablesManager'],
                    scripts: []
                },
                'ocr': {
                    init: this.initOCRPage.bind(this),
                    dependencies: [],
                    scripts: []
                },
                'raporty': {
                    init: this.initReportsPage.bind(this),
                    dependencies: ['ChartsManager', 'TablesManager'],
                    scripts: []
                },
                'ustawienia': {
                    init: this.initSettingsPage.bind(this),
                    dependencies: [],
                    scripts: []
                }
            };
        },

        /**
         * Initialize current page
         */
        initializeCurrentPage: function() {
            const pageModule = this.pageModules[this.currentPage];
            
            if (pageModule) {
                this.loadPageDependencies(pageModule)
                    .then(() => {
                        return this.loadPageScripts(pageModule);
                    })
                    .then(() => {
                        pageModule.init();
                        this.triggerPageEvent('pageInitialized', { page: this.currentPage });
                    })
                    .catch(error => {
                        console.error(`Failed to initialize page ${this.currentPage}:`, error);
                        this.handlePageError(error);
                    });
            } else {
                // Generic page initialization
                this.initGenericPage();
            }
        },

        /**
         * Load page dependencies
         */
        loadPageDependencies: function(pageModule) {
            const promises = pageModule.dependencies.map(dep => {
                return new Promise((resolve, reject) => {
                    if (window.DependencyManager) {
                        window.DependencyManager.whenReady(dep, (error) => {
                            if (error) {
                                console.warn(`Dependency ${dep} failed to load:`, error);
                                resolve(); // Continue even if dependency fails
                            } else {
                                resolve();
                            }
                        });
                    } else {
                        // Fallback: check if dependency exists
                        if (window[dep]) {
                            resolve();
                        } else {
                            console.warn(`Dependency ${dep} not available`);
                            resolve();
                        }
                    }
                });
            });

            return Promise.all(promises);
        },

        /**
         * Load page-specific scripts
         */
        loadPageScripts: function(pageModule) {
            const promises = pageModule.scripts.map(scriptPath => {
                return this.loadScript(scriptPath);
            });

            return Promise.all(promises);
        },

        /**
         * Load external script
         */
        loadScript: function(src) {
            return new Promise((resolve, reject) => {
                if (this.loadedModules.includes(src)) {
                    resolve();
                    return;
                }

                const script = document.createElement('script');
                script.src = src;
                script.onload = () => {
                    this.loadedModules.push(src);
                    resolve();
                };
                script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
                document.head.appendChild(script);
            });
        },

        /**
         * Setup event listeners
         */
        setupEventListeners: function() {
            // Page visibility change
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    this.handlePageHidden();
                } else {
                    this.handlePageVisible();
                }
            });

            // Window resize
            window.addEventListener('resize', () => {
                this.handleWindowResize();
            });

            // Before unload
            window.addEventListener('beforeunload', () => {
                this.handlePageUnload();
            });
        },

        /**
         * Initialize dashboard page
         */
        initDashboardPage: function() {
            console.log('Initializing dashboard page');
            
            // Initialize charts
            if (window.ChartsManager) {
                window.ChartsManager.refreshCharts();
            }

            // Setup dashboard-specific functionality
            this.setupDashboardCards();
            this.setupDashboardRefresh();
            this.loadDashboardData();
        },

        /**
         * Initialize invoices page
         */
        initInvoicesPage: function() {
            console.log('Initializing invoices page');
            
            // Initialize tables
            if (window.TablesManager) {
                window.TablesManager.refreshTables();
            }

            // Initialize invoice forms
            if (window.InvoiceFormManager) {
                // Already initialized globally
            }

            // Setup invoice-specific functionality
            this.setupInvoiceActions();
            this.setupInvoiceFilters();
        },

        /**
         * Initialize contractors page
         */
        initContractorsPage: function() {
            console.log('Initializing contractors page');
            
            // Initialize tables
            if (window.TablesManager) {
                window.TablesManager.refreshTables();
            }

            // Setup contractor-specific functionality
            this.setupContractorActions();
            this.setupContractorImport();
        },

        /**
         * Initialize OCR page
         */
        initOCRPage: function() {
            console.log('Initializing OCR page');
            
            // Setup OCR-specific functionality
            this.setupOCRUpload();
            this.setupOCRResults();
            this.setupOCRValidation();
        },

        /**
         * Initialize reports page
         */
        initReportsPage: function() {
            console.log('Initializing reports page');
            
            // Initialize charts and tables
            if (window.ChartsManager) {
                window.ChartsManager.refreshCharts();
            }
            if (window.TablesManager) {
                window.TablesManager.refreshTables();
            }

            // Setup reports-specific functionality
            this.setupReportFilters();
            this.setupReportExport();
        },

        /**
         * Initialize settings page
         */
        initSettingsPage: function() {
            console.log('Initializing settings page');
            
            // Setup settings-specific functionality
            this.setupSettingsForms();
            this.setupSettingsValidation();
        },

        /**
         * Initialize generic page
         */
        initGenericPage: function() {
            console.log('Initializing generic page');
            
            // Basic functionality for unknown pages
            this.setupGenericForms();
            this.setupGenericTables();
        },

        /**
         * Setup dashboard cards
         */
        setupDashboardCards: function() {
            const cards = document.querySelectorAll('.dashboard-card, .stats-card');
            
            cards.forEach(card => {
                // Add hover effects
                card.addEventListener('mouseenter', function() {
                    this.classList.add('card-hover');
                });
                
                card.addEventListener('mouseleave', function() {
                    this.classList.remove('card-hover');
                });

                // Setup card actions
                const actionBtn = card.querySelector('.card-action');
                if (actionBtn) {
                    actionBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.handleCardAction(card, actionBtn);
                    });
                }
            });
        },

        /**
         * Setup dashboard refresh
         */
        setupDashboardRefresh: function() {
            const refreshBtn = document.querySelector('[data-refresh-dashboard]');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => {
                    this.refreshDashboard();
                });
            }

            // Auto-refresh every 5 minutes
            setInterval(() => {
                if (!document.hidden) {
                    this.refreshDashboard();
                }
            }, 300000);
        },

        /**
         * Load dashboard data
         */
        loadDashboardData: function() {
            fetch('/api/dashboard/stats/', {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                this.updateDashboardStats(data);
            })
            .catch(error => {
                console.error('Failed to load dashboard data:', error);
            });
        },

        /**
         * Update dashboard statistics
         */
        updateDashboardStats: function(data) {
            // Update stat cards
            Object.entries(data.stats || {}).forEach(([key, value]) => {
                const element = document.querySelector(`[data-stat="${key}"]`);
                if (element) {
                    element.textContent = value;
                }
            });

            // Update charts
            if (data.charts && window.ChartsManager) {
                Object.entries(data.charts).forEach(([chartId, chartData]) => {
                    window.ChartsManager.updateChart(chartId, chartData);
                });
            }
        },

        /**
         * Setup invoice actions
         */
        setupInvoiceActions: function() {
            // Bulk actions
            const bulkActions = document.querySelector('.bulk-actions');
            if (bulkActions) {
                this.setupBulkActions(bulkActions);
            }

            // Quick actions
            document.addEventListener('click', (e) => {
                if (e.target.matches('[data-invoice-action]')) {
                    e.preventDefault();
                    this.handleInvoiceAction(e.target);
                }
            });
        },

        /**
         * Setup OCR upload functionality
         */
        setupOCRUpload: function() {
            const uploadArea = document.querySelector('.ocr-upload-area');
            if (!uploadArea) return;

            // Drag and drop
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('drag-over');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                this.handleOCRFileUpload(e.dataTransfer.files);
            });

            // File input
            const fileInput = uploadArea.querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.addEventListener('change', (e) => {
                    this.handleOCRFileUpload(e.target.files);
                });
            }
        },

        /**
         * Handle OCR file upload
         */
        handleOCRFileUpload: function(files) {
            Array.from(files).forEach(file => {
                if (this.isValidOCRFile(file)) {
                    this.uploadOCRFile(file);
                } else {
                    this.showMessage('Nieprawidłowy typ pliku. Obsługiwane formaty: PDF, JPG, PNG', 'error');
                }
            });
        },

        /**
         * Validate OCR file
         */
        isValidOCRFile: function(file) {
            const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'];
            return validTypes.includes(file.type);
        },

        /**
         * Upload OCR file
         */
        uploadOCRFile: function(file) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('csrfmiddlewaretoken', this.getCSRFToken());

            fetch('/api/ocr/upload/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showMessage('Plik został przesłany do przetwarzania OCR', 'success');
                    this.pollOCRStatus(data.task_id);
                } else {
                    this.showMessage('Błąd podczas przesyłania pliku', 'error');
                }
            })
            .catch(error => {
                console.error('OCR upload failed:', error);
                this.showMessage('Błąd podczas przesyłania pliku', 'error');
            });
        },

        /**
         * Poll OCR processing status
         */
        pollOCRStatus: function(taskId) {
            const pollInterval = setInterval(() => {
                fetch(`/api/ocr/status/${taskId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'completed') {
                            clearInterval(pollInterval);
                            this.showOCRResults(data.results);
                        } else if (data.status === 'failed') {
                            clearInterval(pollInterval);
                            this.showMessage('Przetwarzanie OCR nie powiodło się', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('OCR status check failed:', error);
                        clearInterval(pollInterval);
                    });
            }, 2000);

            // Stop polling after 5 minutes
            setTimeout(() => {
                clearInterval(pollInterval);
            }, 300000);
        },

        /**
         * Handle page visibility change
         */
        handlePageHidden: function() {
            // Pause auto-refresh timers
            this.triggerPageEvent('pageHidden');
        },

        /**
         * Handle page becoming visible
         */
        handlePageVisible: function() {
            // Resume auto-refresh timers
            this.triggerPageEvent('pageVisible');
        },

        /**
         * Handle window resize
         */
        handleWindowResize: function() {
            // Refresh responsive components
            if (window.ChartsManager) {
                setTimeout(() => {
                    window.ChartsManager.refreshCharts();
                }, 100);
            }
        },

        /**
         * Handle page unload
         */
        handlePageUnload: function() {
            // Cleanup timers and save state
            this.triggerPageEvent('pageUnload');
        },

        /**
         * Handle page errors
         */
        handlePageError: function(error) {
            console.error('Page error:', error);
            
            if (window.ErrorHandler) {
                window.ErrorHandler.reportError(
                    `Page initialization error: ${error.message}`,
                    'page',
                    { page: this.currentPage, error: error }
                );
            }
        },

        /**
         * Refresh dashboard
         */
        refreshDashboard: function() {
            this.loadDashboardData();
            
            if (window.ChartsManager) {
                window.ChartsManager.refreshCharts();
            }
        },

        /**
         * Utility methods
         */
        getCSRFToken: function() {
            const token = document.querySelector('meta[name="csrf-token"]');
            return token ? token.getAttribute('content') : '';
        },

        showMessage: function(message, type) {
            if (typeof Toastify !== 'undefined') {
                Toastify({
                    text: message,
                    duration: 5000,
                    gravity: 'top',
                    position: 'right',
                    backgroundColor: type === 'success' ? '#28a745' : '#dc3545'
                }).showToast();
            } else {
                console.log(`${type.toUpperCase()}: ${message}`);
            }
        },

        triggerPageEvent: function(eventType, data) {
            const event = new CustomEvent('page' + eventType.charAt(0).toUpperCase() + eventType.slice(1), {
                detail: { page: this.currentPage, ...data }
            });
            window.dispatchEvent(event);
        },

        /**
         * Public API methods
         */
        getCurrentPage: function() {
            return this.currentPage;
        },

        getPageData: function() {
            return this.pageData;
        },

        setPageData: function(key, value) {
            this.pageData[key] = value;
        }
    };

    // Initialize page manager when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            PageManager.init();
        });
    } else {
        PageManager.init();
    }

    // Make PageManager globally available
    window.PageManager = PageManager;

})();