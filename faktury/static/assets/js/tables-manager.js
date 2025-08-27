/**
 * Tables Manager for FaktuLove Application
 * Manages DataTables initialization and fallback table functionality
 */

(function() {
    'use strict';

    const TablesManager = {
        config: {
            enableFallback: true,
            enableSorting: true,
            enableFiltering: true,
            enablePagination: true,
            pageSize: 25,
            enableResponsive: true
        },

        tables: {},
        tableElements: [],
        failedTables: [],
        dataTablesAvailable: false,

        /**
         * Initialize tables manager
         */
        init: function() {
            this.detectDataTables();
            this.findTableElements();
            this.setupDependencyListeners();
            this.initializeTables();
            console.log('TablesManager initialized');
        },

        /**
         * Detect if DataTables is available
         */
        detectDataTables: function() {
            this.dataTablesAvailable = typeof $ !== 'undefined' && typeof $.fn.DataTable !== 'undefined';
            console.log('DataTables available:', this.dataTablesAvailable);
        },

        /**
         * Find table elements in the DOM
         */
        findTableElements: function() {
            const selectors = [
                'table[data-table]',
                'table.data-table',
                'table.datatable',
                '#dataTable',
                '.table-enhanced'
            ];

            const self = this;
            selectors.forEach(function(selector) {
                const elements = document.querySelectorAll(selector);
                elements.forEach(function(element) {
                    if (!self.tableElements.includes(element)) {
                        self.tableElements.push(element);
                    }
                });
            });

            // Also find regular tables that might benefit from enhancement
            const regularTables = document.querySelectorAll('table:not([data-no-enhance])');
            regularTables.forEach(function(table) {
                if (table.rows.length > 5 && !self.tableElements.includes(table)) {
                    self.tableElements.push(table);
                }
            });

            console.log(`Found ${this.tableElements.length} table elements`);
        },

        /**
         * Setup listeners for dependency availability
         */
        setupDependencyListeners: function() {
            const self = this;

            // Listen for DataTables availability
            window.addEventListener('datatablesReady', function() {
                self.dataTablesAvailable = true;
                self.initializeDataTables();
            });

            // Listen for jQuery availability
            window.addEventListener('jqueryReady', function() {
                setTimeout(function() {
                    self.detectDataTables();
                    if (self.dataTablesAvailable) {
                        self.initializeDataTables();
                    }
                }, 500);
            });

            // Listen for dependency manager events
            window.addEventListener('dependencyManagerDependencyReady', function(event) {
                if (event.detail.name === 'DataTables') {
                    self.dataTablesAvailable = true;
                    self.initializeDataTables();
                } else if (event.detail.name === 'jQuery') {
                    setTimeout(function() {
                        self.detectDataTables();
                        if (self.dataTablesAvailable) {
                            self.initializeDataTables();
                        }
                    }, 500);
                }
            });

            // Periodic check for DataTables
            const checkInterval = setInterval(function() {
                const wasAvailable = self.dataTablesAvailable;
                self.detectDataTables();
                
                if (!wasAvailable && self.dataTablesAvailable) {
                    self.initializeDataTables();
                }
            }, 1000);

            // Stop checking after 30 seconds
            setTimeout(function() {
                clearInterval(checkInterval);
            }, 30000);
        },

        /**
         * Initialize all tables
         */
        initializeTables: function() {
            if (this.dataTablesAvailable) {
                this.initializeDataTables();
            } else {
                this.initializeFallbackTables();
            }
        },

        /**
         * Initialize DataTables
         */
        initializeDataTables: function() {
            const self = this;
            
            this.tableElements.forEach(function(table) {
                if (table.hasAttribute('data-initialized')) return;
                
                try {
                    self.createDataTable(table);
                } catch (error) {
                    console.error('Failed to create DataTable:', error);
                    self.handleTableError(table, error);
                }
            });
        },

        /**
         * Create DataTable instance
         */
        createDataTable: function(table) {
            const tableId = table.id || 'table-' + Date.now();
            
            // Get table configuration
            const config = this.getDataTableConfig(table);
            
            // Initialize DataTable
            const dataTable = $(table).DataTable(config);
            
            // Store table reference
            this.tables[tableId] = dataTable;
            table.setAttribute('data-initialized', 'true');
            table.setAttribute('data-table-id', tableId);
            
            console.log(`DataTable created: ${tableId}`);
            
            // Setup additional features
            this.setupTableFeatures(table, dataTable);
            
            // Trigger table created event
            this.triggerTableEvent('tableCreated', {
                id: tableId,
                element: table,
                dataTable: dataTable
            });
        },

        /**
         * Get DataTable configuration
         */
        getDataTableConfig: function(table) {
            const config = {
                responsive: this.config.enableResponsive,
                pageLength: parseInt(table.getAttribute('data-page-size')) || this.config.pageSize,
                searching: this.config.enableFiltering,
                ordering: this.config.enableSorting,
                paging: this.config.enablePagination,
                info: true,
                autoWidth: false,
                language: {
                    search: "Szukaj:",
                    lengthMenu: "Pokaż _MENU_ wpisów",
                    info: "Pokazano _START_ do _END_ z _TOTAL_ wpisów",
                    infoEmpty: "Pokazano 0 do 0 z 0 wpisów",
                    infoFiltered: "(filtrowane z _MAX_ wszystkich wpisów)",
                    paginate: {
                        first: "Pierwsza",
                        last: "Ostatnia",
                        next: "Następna",
                        previous: "Poprzednia"
                    },
                    emptyTable: "Brak danych w tabeli",
                    zeroRecords: "Nie znaleziono pasujących rekordów"
                }
            };

            // Custom column configuration
            const columns = this.getColumnConfig(table);
            if (columns.length > 0) {
                config.columnDefs = columns;
            }

            // Custom ordering
            const defaultOrder = table.getAttribute('data-order');
            if (defaultOrder) {
                try {
                    config.order = JSON.parse(defaultOrder);
                } catch (e) {
                    console.warn('Invalid data-order attribute:', defaultOrder);
                }
            }

            // Ajax configuration if specified
            const ajaxUrl = table.getAttribute('data-ajax');
            if (ajaxUrl) {
                config.ajax = {
                    url: ajaxUrl,
                    type: 'GET',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                };
                config.serverSide = true;
            }

            return config;
        },

        /**
         * Get column configuration from table headers
         */
        getColumnConfig: function(table) {
            const columns = [];
            const headers = table.querySelectorAll('th');
            
            headers.forEach(function(header, index) {
                const columnConfig = { targets: index };
                
                // Check for sortable attribute
                if (header.hasAttribute('data-sortable') && header.getAttribute('data-sortable') === 'false') {
                    columnConfig.orderable = false;
                }
                
                // Check for searchable attribute
                if (header.hasAttribute('data-searchable') && header.getAttribute('data-searchable') === 'false') {
                    columnConfig.searchable = false;
                }
                
                // Check for width
                const width = header.getAttribute('data-width');
                if (width) {
                    columnConfig.width = width;
                }
                
                // Check for type
                const type = header.getAttribute('data-type');
                if (type) {
                    columnConfig.type = type;
                }
                
                if (Object.keys(columnConfig).length > 1) {
                    columns.push(columnConfig);
                }
            });
            
            return columns;
        },

        /**
         * Setup additional table features
         */
        setupTableFeatures: function(table, dataTable) {
            // Add export buttons if requested
            if (table.hasAttribute('data-export')) {
                this.addExportButtons(table, dataTable);
            }
            
            // Add custom search if requested
            if (table.hasAttribute('data-custom-search')) {
                this.addCustomSearch(table, dataTable);
            }
            
            // Add row selection if requested
            if (table.hasAttribute('data-select')) {
                this.addRowSelection(table, dataTable);
            }
        },

        /**
         * Add export buttons to table
         */
        addExportButtons: function(table, dataTable) {
            // This would require DataTables Buttons extension
            // For now, add a simple export button
            const exportBtn = document.createElement('button');
            exportBtn.textContent = 'Export CSV';
            exportBtn.className = 'btn btn-sm btn-outline-secondary';
            exportBtn.addEventListener('click', function() {
                // Simple CSV export
                const csv = dataTable.buttons ? dataTable.button('csv:name').trigger() : null;
                if (!csv) {
                    console.log('Export functionality requires DataTables Buttons extension');
                }
            });
            
            const wrapper = table.closest('.dataTables_wrapper');
            if (wrapper) {
                const toolbar = wrapper.querySelector('.dataTables_filter');
                if (toolbar) {
                    toolbar.appendChild(exportBtn);
                }
            }
        },

        /**
         * Add custom search functionality
         */
        addCustomSearch: function(table, dataTable) {
            const searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.placeholder = 'Szukaj w tabeli...';
            searchInput.className = 'form-control form-control-sm';
            
            searchInput.addEventListener('keyup', function() {
                dataTable.search(this.value).draw();
            });
            
            const wrapper = table.closest('.dataTables_wrapper');
            if (wrapper) {
                const filter = wrapper.querySelector('.dataTables_filter');
                if (filter) {
                    filter.appendChild(searchInput);
                }
            }
        },

        /**
         * Add row selection functionality
         */
        addRowSelection: function(table, dataTable) {
            $(table).on('click', 'tr', function() {
                $(this).toggleClass('selected');
                
                // Trigger selection event
                const selectedRows = dataTable.rows('.selected').data().toArray();
                table.dispatchEvent(new CustomEvent('rowSelectionChanged', {
                    detail: { selectedRows: selectedRows }
                }));
            });
        },

        /**
         * Initialize fallback tables when DataTables is not available
         */
        initializeFallbackTables: function() {
            const self = this;
            
            this.tableElements.forEach(function(table) {
                if (table.hasAttribute('data-initialized')) return;
                
                try {
                    self.createFallbackTable(table);
                } catch (error) {
                    console.error('Failed to create fallback table:', error);
                    self.handleTableError(table, error);
                }
            });
        },

        /**
         * Create fallback table functionality
         */
        createFallbackTable: function(table) {
            const tableId = table.id || 'fallback-table-' + Date.now();
            
            // Add fallback functionality
            this.addFallbackSorting(table);
            this.addFallbackFiltering(table);
            this.addFallbackPagination(table);
            
            table.setAttribute('data-initialized', 'true');
            table.setAttribute('data-fallback', 'true');
            table.classList.add('fallback-table');
            
            console.log(`Fallback table created: ${tableId}`);
            
            // Trigger table created event
            this.triggerTableEvent('fallbackTableCreated', {
                id: tableId,
                element: table
            });
        },

        /**
         * Add fallback sorting functionality
         */
        addFallbackSorting: function(table) {
            if (!this.config.enableSorting) return;
            
            const headers = table.querySelectorAll('th');
            const tbody = table.querySelector('tbody');
            
            if (!tbody) return;
            
            headers.forEach(function(header, columnIndex) {
                if (header.hasAttribute('data-sortable') && header.getAttribute('data-sortable') === 'false') {
                    return;
                }
                
                header.style.cursor = 'pointer';
                header.classList.add('sortable');
                
                header.addEventListener('click', function() {
                    const rows = Array.from(tbody.querySelectorAll('tr'));
                    const isAscending = !header.classList.contains('sort-asc');
                    
                    // Remove sort classes from all headers
                    headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                    
                    // Add sort class to current header
                    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
                    
                    // Sort rows
                    rows.sort(function(a, b) {
                        const aText = a.cells[columnIndex].textContent.trim();
                        const bText = b.cells[columnIndex].textContent.trim();
                        
                        // Try numeric comparison first
                        const aNum = parseFloat(aText);
                        const bNum = parseFloat(bText);
                        
                        if (!isNaN(aNum) && !isNaN(bNum)) {
                            return isAscending ? aNum - bNum : bNum - aNum;
                        }
                        
                        // String comparison
                        return isAscending ? 
                            aText.localeCompare(bText) : 
                            bText.localeCompare(aText);
                    });
                    
                    // Re-append sorted rows
                    rows.forEach(row => tbody.appendChild(row));
                });
            });
        },

        /**
         * Add fallback filtering functionality
         */
        addFallbackFiltering: function(table) {
            if (!this.config.enableFiltering) return;
            
            // Create search input
            const searchContainer = document.createElement('div');
            searchContainer.className = 'table-search mb-3';
            
            const searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.placeholder = 'Szukaj w tabeli...';
            searchInput.className = 'form-control';
            
            searchContainer.appendChild(searchInput);
            table.parentNode.insertBefore(searchContainer, table);
            
            // Add search functionality
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            });
        },

        /**
         * Add fallback pagination functionality
         */
        addFallbackPagination: function(table) {
            if (!this.config.enablePagination) return;
            
            const tbody = table.querySelector('tbody');
            if (!tbody) return;
            
            const rows = Array.from(tbody.querySelectorAll('tr'));
            if (rows.length <= this.config.pageSize) return;
            
            let currentPage = 1;
            const totalPages = Math.ceil(rows.length / this.config.pageSize);
            
            // Create pagination controls
            const paginationContainer = document.createElement('div');
            paginationContainer.className = 'table-pagination mt-3 d-flex justify-content-between align-items-center';
            
            const info = document.createElement('div');
            info.className = 'pagination-info';
            
            const controls = document.createElement('div');
            controls.className = 'pagination-controls';
            
            paginationContainer.appendChild(info);
            paginationContainer.appendChild(controls);
            table.parentNode.appendChild(paginationContainer);
            
            // Show page function
            const showPage = function(page) {
                currentPage = page;
                const start = (page - 1) * this.config.pageSize;
                const end = start + this.config.pageSize;
                
                rows.forEach(function(row, index) {
                    row.style.display = (index >= start && index < end) ? '' : 'none';
                });
                
                // Update info
                const showing = Math.min(end, rows.length);
                info.textContent = `Pokazano ${start + 1} do ${showing} z ${rows.length} wpisów`;
                
                // Update controls
                updateControls();
            }.bind(this);
            
            // Update controls function
            const updateControls = function() {
                controls.innerHTML = '';
                
                // Previous button
                const prevBtn = document.createElement('button');
                prevBtn.textContent = 'Poprzednia';
                prevBtn.className = 'btn btn-sm btn-outline-secondary me-2';
                prevBtn.disabled = currentPage === 1;
                prevBtn.addEventListener('click', () => showPage(currentPage - 1));
                controls.appendChild(prevBtn);
                
                // Page numbers
                for (let i = 1; i <= totalPages; i++) {
                    if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                        const pageBtn = document.createElement('button');
                        pageBtn.textContent = i;
                        pageBtn.className = `btn btn-sm ${i === currentPage ? 'btn-primary' : 'btn-outline-secondary'} me-1`;
                        pageBtn.addEventListener('click', () => showPage(i));
                        controls.appendChild(pageBtn);
                    } else if (i === currentPage - 3 || i === currentPage + 3) {
                        const ellipsis = document.createElement('span');
                        ellipsis.textContent = '...';
                        ellipsis.className = 'me-1';
                        controls.appendChild(ellipsis);
                    }
                }
                
                // Next button
                const nextBtn = document.createElement('button');
                nextBtn.textContent = 'Następna';
                nextBtn.className = 'btn btn-sm btn-outline-secondary ms-2';
                nextBtn.disabled = currentPage === totalPages;
                nextBtn.addEventListener('click', () => showPage(currentPage + 1));
                controls.appendChild(nextBtn);
            };
            
            // Initialize first page
            showPage(1);
        },

        /**
         * Handle table creation errors
         */
        handleTableError: function(table, error) {
            this.failedTables.push({
                element: table,
                error: error,
                timestamp: new Date().toISOString()
            });

            console.error('Table initialization failed:', error);
            
            // Add error indicator
            table.classList.add('table-error');
            
            // Report to error handler
            if (window.ErrorHandler) {
                window.ErrorHandler.reportError(
                    `Table initialization failed: ${error.message}`,
                    'table',
                    { element: table, error: error }
                );
            }

            this.triggerTableEvent('tableError', {
                element: table,
                error: error
            });
        },

        /**
         * Initialize specific table
         */
        initializeTable: function(tableSelector) {
            const table = document.querySelector(tableSelector);
            if (table) {
                if (this.dataTablesAvailable) {
                    this.createDataTable(table);
                } else {
                    this.createFallbackTable(table);
                }
            }
        },

        /**
         * Destroy table
         */
        destroyTable: function(tableId) {
            const table = this.tables[tableId];
            if (table && table.destroy) {
                table.destroy();
                delete this.tables[tableId];
                
                this.triggerTableEvent('tableDestroyed', {
                    id: tableId
                });
            }
        },

        /**
         * Refresh all tables
         */
        refreshTables: function() {
            // Re-detect DataTables
            this.detectDataTables();
            
            // Re-initialize tables
            this.tableElements.forEach(function(table) {
                table.removeAttribute('data-initialized');
            });
            
            this.initializeTables();
        },

        /**
         * Get CSRF token
         */
        getCSRFToken: function() {
            const token = document.querySelector('meta[name="csrf-token"]');
            return token ? token.getAttribute('content') : '';
        },

        /**
         * Trigger table events
         */
        triggerTableEvent: function(eventType, data) {
            const event = new CustomEvent('tables' + eventType.charAt(0).toUpperCase() + eventType.slice(1), {
                detail: data
            });
            window.dispatchEvent(event);
        },

        /**
         * Get table statistics
         */
        getStats: function() {
            return {
                totalTables: this.tableElements.length,
                initializedTables: Object.keys(this.tables).length,
                failedTables: this.failedTables.length,
                dataTablesAvailable: this.dataTablesAvailable,
                fallbackTables: this.tableElements.filter(el => el.hasAttribute('data-fallback')).length
            };
        }
    };

    // Initialize tables manager when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            TablesManager.init();
        });
    } else {
        TablesManager.init();
    }

    // Make TablesManager globally available
    window.TablesManager = TablesManager;

})();