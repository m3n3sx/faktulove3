/**
 * Advanced Search JavaScript
 * Handles advanced search functionality with Polish business criteria
 */

class AdvancedSearch {
    constructor() {
        this.currentPage = 1;
        this.currentSort = { by: 'data_wystawienia', order: 'desc' };
        this.searchTimeout = null;
        this.currentSearchType = 'invoices';
        
        this.init();
    }
    
    init() {
        this.initDatePickers();
        this.initEventListeners();
        this.loadSavedSearches();
        this.loadSearchHistory();
        this.initSearchSuggestions();
    }
    
    initDatePickers() {
        // Initialize Flatpickr date pickers with Polish locale
        flatpickr('.datepicker', {
            locale: 'pl',
            dateFormat: 'Y-m-d',
            allowInput: true,
            clickOpens: true
        });
    }
    
    initEventListeners() {
        // Search form submission
        document.getElementById('advanced-search-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });
        
        // Search type change
        document.querySelectorAll('input[name="search_type"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentSearchType = e.target.value;
                this.toggleFilters();
                this.performSearch();
            });
        });
        
        // Real-time search on input
        document.getElementById('search-query').addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.performSearch();
            }, 500);
        });
        
        // OCR confidence slider
        const ocrSlider = document.getElementById('ocr-confidence');
        const ocrValue = document.getElementById('ocr-confidence-value');
        ocrSlider.addEventListener('input', (e) => {
            ocrValue.textContent = e.target.value + '%';
        });
        
        // Clear search
        document.getElementById('clear-search').addEventListener('click', () => {
            document.getElementById('search-query').value = '';
            this.performSearch();
        });
        
        // Clear filters
        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });
        
        // Save search
        document.getElementById('save-search').addEventListener('click', () => {
            this.showSaveSearchModal();
        });
        
        // Confirm save search
        document.getElementById('confirm-save-search').addEventListener('click', () => {
            this.saveSearch();
        });
        
        // Sort options
        document.querySelectorAll('.sort-option').forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const sortBy = e.target.dataset.sort;
                const sortOrder = e.target.dataset.order;
                this.setSorting(sortBy, sortOrder);
            });
        });
        
        // Export results
        document.getElementById('export-results').addEventListener('click', () => {
            this.exportResults();
        });
        
        // Filter changes
        const filterInputs = document.querySelectorAll('#advanced-search-form input, #advanced-search-form select');
        filterInputs.forEach(input => {
            if (input.id !== 'search-query') {
                input.addEventListener('change', () => {
                    clearTimeout(this.searchTimeout);
                    this.searchTimeout = setTimeout(() => {
                        this.performSearch();
                    }, 300);
                });
            }
        });
    }
    
    initSearchSuggestions() {
        const searchInput = document.getElementById('search-query');
        const suggestionsContainer = document.getElementById('search-suggestions');
        
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            if (query.length >= 2) {
                this.getSuggestions(query);
            } else {
                suggestionsContainer.style.display = 'none';
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#search-query') && !e.target.closest('#search-suggestions')) {
                suggestionsContainer.style.display = 'none';
            }
        });
    }
    
    toggleFilters() {
        const invoiceFilters = document.getElementById('invoice-filters');
        const companyFilters = document.getElementById('company-filters');
        
        if (this.currentSearchType === 'invoices') {
            invoiceFilters.style.display = 'block';
            companyFilters.style.display = 'none';
        } else {
            invoiceFilters.style.display = 'none';
            companyFilters.style.display = 'block';
        }
    }
    
    async getSuggestions(query) {
        try {
            const response = await fetch(`/api/search/suggestions/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.displaySuggestions(data.suggestions);
        } catch (error) {
            console.error('Error getting suggestions:', error);
        }
    }
    
    displaySuggestions(suggestions) {
        const container = document.getElementById('search-suggestions');
        
        if (suggestions.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        container.innerHTML = suggestions.map(suggestion => 
            `<a class="dropdown-item" href="#" onclick="advancedSearch.selectSuggestion('${suggestion}')">${suggestion}</a>`
        ).join('');
        
        container.style.display = 'block';
    }
    
    selectSuggestion(suggestion) {
        document.getElementById('search-query').value = suggestion;
        document.getElementById('search-suggestions').style.display = 'none';
        this.performSearch();
    }
    
    async performSearch(page = 1) {
        this.currentPage = page;
        this.showLoading();
        
        try {
            const formData = new FormData(document.getElementById('advanced-search-form'));
            const searchData = {
                query: formData.get('query') || '',
                page: page,
                per_page: 20,
                sort_by: this.currentSort.by,
                sort_order: this.currentSort.order,
                filters: this.getFilters(formData)
            };
            
            const endpoint = this.currentSearchType === 'invoices' 
                ? '/api/search/invoices/' 
                : '/api/search/companies/';
            
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(searchData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.displayResults(data);
                this.updatePagination(data);
                this.updateResultsCount(data);
            } else {
                this.showError(data.error || 'Wystąpił błąd podczas wyszukiwania');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Wystąpił błąd podczas wyszukiwania');
        } finally {
            this.hideLoading();
        }
    }
    
    getFilters(formData) {
        const filters = {};
        
        if (this.currentSearchType === 'invoices') {
            // Date filters
            if (formData.get('date_from')) filters.date_from = formData.get('date_from');
            if (formData.get('date_to')) filters.date_to = formData.get('date_to');
            
            // Amount filters
            if (formData.get('amount_from')) filters.amount_from = parseFloat(formData.get('amount_from'));
            if (formData.get('amount_to')) filters.amount_to = parseFloat(formData.get('amount_to'));
            
            // Status filter
            const statusValues = formData.getAll('status');
            if (statusValues.length > 0) filters.status = statusValues;
            
            // Document type filter
            const docTypeValues = formData.getAll('typ_dokumentu');
            if (docTypeValues.length > 0) filters.typ_dokumentu = docTypeValues;
            
            // Invoice type filter
            if (formData.get('typ_faktury')) filters.typ_faktury = formData.get('typ_faktury');
            
            // OCR confidence filter
            const ocrConfidence = formData.get('ocr_confidence_min');
            if (ocrConfidence && ocrConfidence > 0) filters.ocr_confidence_min = parseFloat(ocrConfidence);
            
            // Boolean filters
            if (formData.get('overdue')) filters.overdue = true;
            if (formData.get('manual_verification_required')) filters.manual_verification_required = true;
        } else {
            // Company filters
            if (formData.get('czy_firma')) filters.czy_firma = formData.get('czy_firma') === 'true';
            if (formData.get('miasto')) filters.miasto = formData.get('miasto');
            if (formData.get('has_nip')) filters.has_nip = true;
            if (formData.get('has_email')) filters.has_email = true;
        }
        
        return filters;
    }
    
    displayResults(data) {
        const container = document.getElementById('search-results');
        
        if (data.results.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="fas fa-search fa-3x mb-3"></i>
                    <p>Nie znaleziono wyników dla podanych kryteriów</p>
                </div>
            `;
            return;
        }
        
        if (this.currentSearchType === 'invoices') {
            this.displayInvoiceResults(data.results);
        } else {
            this.displayCompanyResults(data.results);
        }
    }
    
    displayInvoiceResults(results) {
        const container = document.getElementById('search-results');
        
        const html = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Numer</th>
                            <th>Typ</th>
                            <th>Data wystawienia</th>
                            <th>Nabywca</th>
                            <th>Status</th>
                            <th>OCR</th>
                            <th>Akcje</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(invoice => `
                            <tr>
                                <td>
                                    <strong>${invoice.numer}</strong>
                                    <br>
                                    <small class="text-muted">${invoice.typ_dokumentu}</small>
                                </td>
                                <td>
                                    <span class="badge bg-${invoice.typ_faktury === 'Sprzedaż' ? 'success' : 'info'}">
                                        ${invoice.typ_faktury}
                                    </span>
                                </td>
                                <td>
                                    ${this.formatDate(invoice.data_wystawienia)}
                                    <br>
                                    <small class="text-muted">Termin: ${this.formatDate(invoice.termin_platnosci)}</small>
                                </td>
                                <td>
                                    <strong>${invoice.nabywca.nazwa}</strong>
                                    <br>
                                    <small class="text-muted">
                                        ${invoice.nabywca.nip ? `NIP: ${invoice.nabywca.nip}` : ''}
                                        ${invoice.nabywca.miejscowosc}
                                    </small>
                                </td>
                                <td>
                                    <span class="badge bg-${this.getStatusColor(invoice.status)}">
                                        ${invoice.status}
                                    </span>
                                </td>
                                <td>
                                    ${invoice.ocr_confidence ? `
                                        <div class="progress" style="height: 20px;">
                                            <div class="progress-bar bg-${this.getConfidenceColor(invoice.ocr_confidence)}" 
                                                 style="width: ${invoice.ocr_confidence}%">
                                                ${Math.round(invoice.ocr_confidence)}%
                                            </div>
                                        </div>
                                        ${invoice.manual_verification_required ? 
                                            '<small class="text-warning"><i class="fas fa-exclamation-triangle"></i> Wymaga weryfikacji</small>' : 
                                            ''
                                        }
                                    ` : '<span class="text-muted">-</span>'}
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <a href="${invoice.url}" class="btn btn-outline-primary">
                                            <i class="fas fa-eye"></i>
                                        </a>
                                        <a href="${invoice.url}edit/" class="btn btn-outline-secondary">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    displayCompanyResults(results) {
        const container = document.getElementById('search-results');
        
        const html = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Nazwa</th>
                            <th>NIP</th>
                            <th>Lokalizacja</th>
                            <th>Typ</th>
                            <th>Kontakt</th>
                            <th>Akcje</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(company => `
                            <tr>
                                <td>
                                    <strong>${company.nazwa}</strong>
                                    ${company.regon ? `<br><small class="text-muted">REGON: ${company.regon}</small>` : ''}
                                </td>
                                <td>
                                    ${company.nip ? `
                                        <code>${company.nip}</code>
                                    ` : '<span class="text-muted">-</span>'}
                                </td>
                                <td>
                                    ${company.miejscowosc}
                                    <br>
                                    <small class="text-muted">${company.ulica}</small>
                                    <br>
                                    <small class="text-muted">${company.kod_pocztowy}</small>
                                </td>
                                <td>
                                    <span class="badge bg-${company.czy_firma ? 'primary' : 'secondary'}">
                                        ${company.czy_firma ? 'Firma' : 'Osoba fizyczna'}
                                    </span>
                                </td>
                                <td>
                                    ${company.email ? `
                                        <a href="mailto:${company.email}">${company.email}</a><br>
                                    ` : ''}
                                    ${company.telefon ? `
                                        <a href="tel:${company.telefon}">${company.telefon}</a>
                                    ` : ''}
                                    ${!company.email && !company.telefon ? '<span class="text-muted">-</span>' : ''}
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <a href="${company.url}" class="btn btn-outline-primary">
                                            <i class="fas fa-eye"></i>
                                        </a>
                                        <a href="${company.url}edit/" class="btn btn-outline-secondary">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    updatePagination(data) {
        const container = document.getElementById('pagination-container');
        const pagination = document.getElementById('pagination');
        
        if (data.total_pages <= 1) {
            container.style.display = 'none';
            return;
        }
        
        container.style.display = 'block';
        
        let html = '';
        
        // Previous button
        if (data.has_previous) {
            html += `<li class="page-item">
                <a class="page-link" href="#" onclick="advancedSearch.performSearch(${data.page - 1})">Poprzednia</a>
            </li>`;
        }
        
        // Page numbers
        const startPage = Math.max(1, data.page - 2);
        const endPage = Math.min(data.total_pages, data.page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === data.page ? 'active' : ''}">
                <a class="page-link" href="#" onclick="advancedSearch.performSearch(${i})">${i}</a>
            </li>`;
        }
        
        // Next button
        if (data.has_next) {
            html += `<li class="page-item">
                <a class="page-link" href="#" onclick="advancedSearch.performSearch(${data.page + 1})">Następna</a>
            </li>`;
        }
        
        pagination.innerHTML = html;
    }
    
    updateResultsCount(data) {
        const countElement = document.getElementById('results-count');
        const type = this.currentSearchType === 'invoices' ? 'faktur' : 'kontrahentów';
        countElement.textContent = `Znaleziono ${data.total_count} ${type}`;
    }
    
    setSorting(sortBy, sortOrder) {
        this.currentSort = { by: sortBy, order: sortOrder };
        this.performSearch(this.currentPage);
    }
    
    clearFilters() {
        const form = document.getElementById('advanced-search-form');
        const inputs = form.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        
        // Reset search type to invoices
        document.getElementById('search-invoices').checked = true;
        this.currentSearchType = 'invoices';
        this.toggleFilters();
        
        // Reset OCR confidence slider
        document.getElementById('ocr-confidence').value = 0;
        document.getElementById('ocr-confidence-value').textContent = '0%';
        
        this.performSearch();
    }
    
    showSaveSearchModal() {
        const modal = new bootstrap.Modal(document.getElementById('saveSearchModal'));
        modal.show();
    }
    
    async saveSearch() {
        const name = document.getElementById('search-name').value.trim();
        
        if (!name) {
            alert('Podaj nazwę wyszukiwania');
            return;
        }
        
        try {
            const formData = new FormData(document.getElementById('advanced-search-form'));
            const searchData = {
                name: name,
                query: formData.get('query') || '',
                filters: this.getFilters(formData)
            };
            
            const response = await fetch('/api/search/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(searchData)
            });
            
            if (response.ok) {
                bootstrap.Modal.getInstance(document.getElementById('saveSearchModal')).hide();
                document.getElementById('search-name').value = '';
                this.loadSavedSearches();
                this.showSuccess('Wyszukiwanie zostało zapisane');
            } else {
                const data = await response.json();
                alert(data.error || 'Wystąpił błąd podczas zapisywania');
            }
        } catch (error) {
            console.error('Error saving search:', error);
            alert('Wystąpił błąd podczas zapisywania');
        }
    }
    
    async loadSavedSearches() {
        try {
            const response = await fetch('/api/search/saved/');
            const data = await response.json();
            
            const container = document.getElementById('saved-searches-list');
            
            if (data.saved_searches.length === 0) {
                container.innerHTML = '<small class="text-muted">Brak zapisanych wyszukiwań</small>';
                return;
            }
            
            container.innerHTML = data.saved_searches.map(search => `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <a href="#" class="text-decoration-none" onclick="advancedSearch.loadSavedSearch('${search.name}')">
                        <small>${search.name}</small>
                    </a>
                    <button class="btn btn-sm btn-outline-danger" onclick="advancedSearch.deleteSavedSearch('${search.name}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading saved searches:', error);
        }
    }
    
    async loadSearchHistory() {
        try {
            const response = await fetch('/api/search/history/');
            const data = await response.json();
            
            const container = document.getElementById('search-history-list');
            
            if (data.history.length === 0) {
                container.innerHTML = '<small class="text-muted">Brak historii wyszukiwań</small>';
                return;
            }
            
            container.innerHTML = data.history.slice(0, 5).map(entry => `
                <div class="mb-2">
                    <a href="#" class="text-decoration-none" onclick="advancedSearch.loadHistoryEntry('${entry.query}')">
                        <small>${entry.query || 'Wyszukiwanie z filtrami'}</small>
                    </a>
                    <br>
                    <small class="text-muted">${entry.result_count} wyników</small>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading search history:', error);
        }
    }
    
    async deleteSavedSearch(name) {
        if (!confirm('Czy na pewno chcesz usunąć to zapisane wyszukiwanie?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/search/saved/${encodeURIComponent(name)}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                this.loadSavedSearches();
                this.showSuccess('Zapisane wyszukiwanie zostało usunięte');
            } else {
                alert('Wystąpił błąd podczas usuwania');
            }
        } catch (error) {
            console.error('Error deleting saved search:', error);
            alert('Wystąpił błąd podczas usuwania');
        }
    }
    
    loadSavedSearch(name) {
        // Implementation would load the saved search criteria
        console.log('Loading saved search:', name);
    }
    
    loadHistoryEntry(query) {
        document.getElementById('search-query').value = query;
        this.performSearch();
    }
    
    async exportResults() {
        // Implementation for exporting search results
        console.log('Exporting results...');
        alert('Funkcja eksportu będzie dostępna wkrótce');
    }
    
    showLoading() {
        document.getElementById('loading-indicator').style.display = 'block';
        document.getElementById('search-results').style.display = 'none';
    }
    
    hideLoading() {
        document.getElementById('loading-indicator').style.display = 'none';
        document.getElementById('search-results').style.display = 'block';
    }
    
    showError(message) {
        const container = document.getElementById('search-results');
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                ${message}
            </div>
        `;
    }
    
    showSuccess(message) {
        // Create a temporary success message
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pl-PL');
    }
    
    getStatusColor(status) {
        const colors = {
            'Wystawiona': 'warning',
            'Opłacona': 'success',
            'Częściowo opłacona': 'info',
            'Anulowana': 'danger'
        };
        return colors[status] || 'secondary';
    }
    
    getConfidenceColor(confidence) {
        if (confidence >= 90) return 'success';
        if (confidence >= 70) return 'warning';
        return 'danger';
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.advancedSearch = new AdvancedSearch();
});