/**
 * Data Export and Import JavaScript
 * Handles data export/import functionality with progress tracking
 */

class DataExportImport {
    constructor() {
        this.progressIntervals = {};
        this.init();
    }
    
    init() {
        this.initEventListeners();
        this.loadStatistics();
        this.setupFileUpload();
    }
    
    initEventListeners() {
        // Export form submission
        document.getElementById('export-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleExport();
        });
        
        // Import form submission
        document.getElementById('import-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleImport();
        });
        
        // Restore form submission
        document.getElementById('restore-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRestore();
        });
        
        // Create backup button
        document.getElementById('create-backup').addEventListener('click', () => {
            this.handleCreateBackup();
        });
        
        // Download template button
        document.getElementById('download-template').addEventListener('click', () => {
            this.downloadTemplate();
        });
        
        // Data type change for export
        document.querySelectorAll('input[name="export_data_type"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.toggleExportFilters(e.target.value);
            });
        });
        
        // Format change for export (disable PDF for products)
        document.getElementById('export-format').addEventListener('change', (e) => {
            this.validateExportFormat();
        });
        
        // File input changes
        document.getElementById('import-file').addEventListener('change', (e) => {
            this.handleFileSelect(e.target);
            this.validateImportForm();
        });
        
        document.getElementById('restore-file').addEventListener('change', (e) => {
            this.validateRestoreForm();
        });
    }
    
    setupFileUpload() {
        const uploadArea = document.getElementById('file-upload-area');
        const fileInput = document.getElementById('import-file');
        
        // Drag and drop functionality
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                this.handleFileSelect(fileInput);
                this.validateImportForm();
            }
        });
        
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
    }
    
    toggleExportFilters(dataType) {
        const invoiceFilters = document.getElementById('invoice-export-filters');
        const companyFilters = document.getElementById('company-export-filters');
        
        if (dataType === 'invoices') {
            invoiceFilters.style.display = 'block';
            companyFilters.style.display = 'none';
        } else if (dataType === 'companies') {
            invoiceFilters.style.display = 'none';
            companyFilters.style.display = 'block';
        } else {
            invoiceFilters.style.display = 'none';
            companyFilters.style.display = 'none';
        }
        
        this.validateExportFormat();
    }
    
    validateExportFormat() {
        const dataType = document.querySelector('input[name="export_data_type"]:checked').value;
        const formatSelect = document.getElementById('export-format');
        
        // Disable PDF for products (too many columns)
        const pdfOption = formatSelect.querySelector('option[value="pdf"]');
        if (dataType === 'products') {
            pdfOption.disabled = true;
            if (formatSelect.value === 'pdf') {
                formatSelect.value = 'excel';
            }
        } else {
            pdfOption.disabled = false;
        }
    }
    
    handleFileSelect(input) {
        const uploadArea = document.getElementById('file-upload-area');
        const uploadText = uploadArea.querySelector('.file-upload-text');
        
        if (input.files.length > 0) {
            const file = input.files[0];
            uploadText.innerHTML = `
                <i class="fas fa-file fa-2x mb-2 text-success"></i>
                <p><strong>${file.name}</strong></p>
                <small class="text-muted">Rozmiar: ${this.formatFileSize(file.size)}</small>
            `;
            uploadArea.classList.add('file-selected');
        } else {
            uploadText.innerHTML = `
                <i class="fas fa-cloud-upload-alt fa-2x mb-2"></i>
                <p>Przeciągnij plik tutaj lub kliknij aby wybrać</p>
                <small class="text-muted">Obsługiwane formaty: CSV, Excel, JSON</small>
            `;
            uploadArea.classList.remove('file-selected');
        }
    }
    
    validateImportForm() {
        const fileInput = document.getElementById('import-file');
        const submitButton = document.querySelector('#import-form button[type="submit"]');
        
        submitButton.disabled = fileInput.files.length === 0;
    }
    
    validateRestoreForm() {
        const fileInput = document.getElementById('restore-file');
        const submitButton = document.querySelector('#restore-form button[type="submit"]');
        
        submitButton.disabled = fileInput.files.length === 0;
    }
    
    async handleExport() {
        try {
            const formData = new FormData(document.getElementById('export-form'));
            const dataType = formData.get('export_data_type');
            const format = formData.get('format');
            
            // Prepare export data
            const exportData = {
                format: format,
                filters: this.getExportFilters(formData, dataType)
            };
            
            // Show progress
            this.showProgress('export', 0, 'Rozpoczynanie eksportu...');
            
            // Determine API endpoint
            let endpoint;
            switch (dataType) {
                case 'invoices':
                    endpoint = '/api/export/invoices/';
                    break;
                case 'companies':
                    endpoint = '/api/export/companies/';
                    break;
                case 'products':
                    endpoint = '/api/export/products/';
                    break;
                default:
                    throw new Error('Nieobsługiwany typ danych');
            }
            
            // Make export request
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(exportData)
            });
            
            if (response.ok) {
                // Handle file download
                const blob = await response.blob();
                const filename = this.getFilenameFromResponse(response) || 
                                `export_${dataType}_${new Date().toISOString().slice(0, 10)}.${format}`;
                
                this.downloadFile(blob, filename);
                this.hideProgress('export');
                this.showSuccess('Eksport zakończony pomyślnie');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Błąd eksportu');
            }
            
        } catch (error) {
            console.error('Export error:', error);
            this.hideProgress('export');
            this.showError(error.message);
        }
    }
    
    async handleImport() {
        try {
            const formData = new FormData(document.getElementById('import-form'));
            
            // Show progress
            this.showProgress('import', 0, 'Rozpoczynanie importu...');
            
            // Make import request
            const response = await fetch('/api/import/data/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });
            
            const result = await response.json();
            
            this.hideProgress('import');
            
            if (result.success) {
                this.showImportResults(result);
                this.loadStatistics(); // Refresh statistics
            } else {
                this.showImportErrors(result);
            }
            
        } catch (error) {
            console.error('Import error:', error);
            this.hideProgress('import');
            this.showError('Wystąpił błąd podczas importu danych');
        }
    }
    
    async handleRestore() {
        try {
            if (!confirm('Czy na pewno chcesz przywrócić dane z kopii zapasowej? Ta operacja może nadpisać istniejące dane.')) {
                return;
            }
            
            const formData = new FormData(document.getElementById('restore-form'));
            
            // Show progress
            this.showProgress('restore', 0, 'Rozpoczynanie przywracania...');
            
            // Make restore request
            const response = await fetch('/api/restore/backup/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });
            
            const result = await response.json();
            
            this.hideProgress('restore');
            
            if (result.success) {
                this.showRestoreResults(result);
                this.loadStatistics(); // Refresh statistics
            } else {
                this.showError(result.errors ? result.errors.join(', ') : 'Błąd przywracania');
            }
            
        } catch (error) {
            console.error('Restore error:', error);
            this.hideProgress('restore');
            this.showError('Wystąpił błąd podczas przywracania danych');
        }
    }
    
    async handleCreateBackup() {
        try {
            const includeFiles = document.getElementById('include-files').checked;
            
            // Show progress
            this.showProgress('backup', 0, 'Tworzenie kopii zapasowej...');
            
            // Make backup request
            const response = await fetch('/api/create/backup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    include_files: includeFiles
                })
            });
            
            if (response.ok) {
                // Handle file download
                const blob = await response.blob();
                const filename = this.getFilenameFromResponse(response) || 
                                `backup_${new Date().toISOString().slice(0, 10)}.zip`;
                
                this.downloadFile(blob, filename);
                this.hideProgress('backup');
                this.showSuccess('Kopia zapasowa utworzona pomyślnie');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Błąd tworzenia kopii zapasowej');
            }
            
        } catch (error) {
            console.error('Backup error:', error);
            this.hideProgress('backup');
            this.showError(error.message);
        }
    }
    
    async downloadTemplate() {
        try {
            const dataType = document.querySelector('input[name="export_data_type"]:checked').value;
            const format = 'excel'; // Templates are always Excel
            
            const response = await fetch(`/api/export/templates/?type=${dataType}&format=${format}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const filename = `szablon_${dataType}.xlsx`;
                this.downloadFile(blob, filename);
            } else {
                throw new Error('Błąd pobierania szablonu');
            }
            
        } catch (error) {
            console.error('Template download error:', error);
            this.showError(error.message);
        }
    }
    
    getExportFilters(formData, dataType) {
        const filters = {};
        
        if (dataType === 'invoices') {
            if (formData.get('date_from')) filters.date_from = formData.get('date_from');
            if (formData.get('date_to')) filters.date_to = formData.get('date_to');
            
            const status = formData.getAll('status');
            if (status.length > 0) filters.status = status;
            
            const docType = formData.getAll('typ_dokumentu');
            if (docType.length > 0) filters.typ_dokumentu = docType;
        } else if (dataType === 'companies') {
            if (formData.get('czy_firma')) filters.czy_firma = formData.get('czy_firma') === 'true';
            if (formData.get('miasto')) filters.miasto = formData.get('miasto');
        }
        
        return filters;
    }
    
    showProgress(type, progress, message) {
        const progressContainer = document.getElementById(`${type}-progress`);
        const progressBar = progressContainer.querySelector('.progress-bar');
        const progressText = document.getElementById(`${type}-progress-text`);
        
        progressContainer.style.display = 'block';
        progressBar.style.width = `${progress}%`;
        progressBar.textContent = `${progress}%`;
        progressText.textContent = message;
        
        // Start progress polling if not already started
        if (!this.progressIntervals[type]) {
            this.startProgressPolling(type);
        }
    }
    
    hideProgress(type) {
        const progressContainer = document.getElementById(`${type}-progress`);
        progressContainer.style.display = 'none';
        
        // Stop progress polling
        if (this.progressIntervals[type]) {
            clearInterval(this.progressIntervals[type]);
            delete this.progressIntervals[type];
        }
    }
    
    startProgressPolling(type) {
        // This would poll the server for progress updates
        // For now, we'll simulate progress
        let progress = 0;
        this.progressIntervals[type] = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 90) {
                progress = 90; // Don't go to 100% until operation completes
            }
            
            const progressBar = document.querySelector(`#${type}-progress .progress-bar`);
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
                progressBar.textContent = `${Math.round(progress)}%`;
            }
        }, 500);
    }
    
    showImportResults(result) {
        const resultsContainer = document.getElementById('import-results');
        
        let html = `
            <div class="alert alert-success">
                <h6><i class="fas fa-check-circle"></i> Import zakończony pomyślnie</h6>
                <ul class="mb-0">
                    <li>Zaimportowano: ${result.imported_count} rekordów</li>
                    <li>Zaktualizowano: ${result.updated_count} rekordów</li>
                    <li>Pominięto: ${result.skipped_count} rekordów</li>
                </ul>
            </div>
        `;
        
        if (result.warnings && result.warnings.length > 0) {
            html += `
                <div class="alert alert-warning">
                    <h6><i class="fas fa-exclamation-triangle"></i> Ostrzeżenia</h6>
                    <ul class="mb-0">
                        ${result.warnings.map(warning => `<li>${warning}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        resultsContainer.innerHTML = html;
        resultsContainer.style.display = 'block';
    }
    
    showImportErrors(result) {
        const resultsContainer = document.getElementById('import-results');
        
        let html = `
            <div class="alert alert-danger">
                <h6><i class="fas fa-exclamation-circle"></i> Błędy importu</h6>
                <ul class="mb-0">
                    ${result.errors.map(error => `<li>${error}</li>`).join('')}
                </ul>
            </div>
        `;
        
        if (result.warnings && result.warnings.length > 0) {
            html += `
                <div class="alert alert-warning">
                    <h6><i class="fas fa-exclamation-triangle"></i> Ostrzeżenia</h6>
                    <ul class="mb-0">
                        ${result.warnings.map(warning => `<li>${warning}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        resultsContainer.innerHTML = html;
        resultsContainer.style.display = 'block';
    }
    
    showRestoreResults(result) {
        let message = 'Przywracanie zakończone pomyślnie.\n\n';
        
        if (result.imported) {
            if (result.imported.invoices) {
                message += `Faktury: ${result.imported.invoices.restored} przywrócono, ${result.imported.invoices.skipped} pominięto\n`;
            }
            if (result.imported.companies) {
                message += `Kontrahenci: ${result.imported.companies.restored} przywrócono, ${result.imported.companies.skipped} pominięto\n`;
            }
            if (result.imported.products) {
                message += `Produkty: ${result.imported.products.restored} przywrócono, ${result.imported.products.skipped} pominięto\n`;
            }
        }
        
        this.showSuccess(message);
    }
    
    async loadStatistics() {
        try {
            const response = await fetch('/api/export/statistics/');
            const stats = await response.json();
            
            document.getElementById('total-invoices').textContent = stats.total_invoices || 0;
            document.getElementById('total-companies').textContent = stats.total_companies || 0;
            document.getElementById('total-products').textContent = stats.total_products || 0;
            
            const totalRecords = (stats.total_invoices || 0) + (stats.total_companies || 0) + (stats.total_products || 0);
            document.getElementById('total-records').textContent = totalRecords;
            
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }
    
    downloadFile(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
    
    getFilenameFromResponse(response) {
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="(.+)"/);
            if (filenameMatch) {
                return filenameMatch[1];
            }
        }
        return null;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showSuccess(message) {
        document.getElementById('success-message').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('successModal'));
        modal.show();
    }
    
    showError(message) {
        document.getElementById('error-message').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        modal.show();
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dataExportImport = new DataExportImport();
});