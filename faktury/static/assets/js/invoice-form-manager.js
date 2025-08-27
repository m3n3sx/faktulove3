/**
 * Invoice Form Manager for FaktuLove Application
 * Manages invoice creation forms, validation, and submission
 */

(function() {
    'use strict';

    const InvoiceFormManager = {
        config: {
            enableAutoSave: true,
            autoSaveInterval: 30000, // 30 seconds
            enableValidation: true,
            enableCalculations: true,
            enableContractorLookup: true
        },

        forms: {},
        activeForm: null,
        autoSaveTimer: null,
        validationRules: {},

        /**
         * Initialize invoice form manager
         */
        init: function() {
            this.findInvoiceForms();
            this.setupEventListeners();
            this.initializeValidation();
            this.setupAutoSave();
            console.log('InvoiceFormManager initialized');
        },

        /**
         * Find invoice forms in the DOM
         */
        findInvoiceForms: function() {
            const selectors = [
                'form[data-invoice-form]',
                'form.invoice-form',
                '#invoice-form',
                'form[action*="invoice"]'
            ];

            const self = this;
            selectors.forEach(function(selector) {
                const forms = document.querySelectorAll(selector);
                forms.forEach(function(form) {
                    const formId = form.id || 'invoice-form-' + Date.now();
                    self.forms[formId] = {
                        element: form,
                        data: {},
                        isDirty: false,
                        isValid: false
                    };
                    
                    if (!self.activeForm) {
                        self.activeForm = formId;
                    }
                });
            });

            console.log(`Found ${Object.keys(this.forms).length} invoice forms`);
        },

        /**
         * Setup event listeners
         */
        setupEventListeners: function() {
            const self = this;

            // Form submission
            Object.values(this.forms).forEach(function(formData) {
                const form = formData.element;
                
                form.addEventListener('submit', function(e) {
                    self.handleFormSubmission(e, form);
                });

                // Input changes
                form.addEventListener('input', function(e) {
                    self.handleInputChange(e, form);
                });

                // Focus events for field validation
                form.addEventListener('focusout', function(e) {
                    self.validateField(e.target, form);
                });
            });

            // Add invoice item buttons
            document.addEventListener('click', function(e) {
                if (e.target.matches('[data-add-item]')) {
                    e.preventDefault();
                    self.addInvoiceItem(e.target);
                }
                
                if (e.target.matches('[data-remove-item]')) {
                    e.preventDefault();
                    self.removeInvoiceItem(e.target);
                }
            });

            // Contractor lookup
            document.addEventListener('input', function(e) {
                if (e.target.matches('[data-contractor-lookup]')) {
                    self.handleContractorLookup(e.target);
                }
            });

            // Before unload warning
            window.addEventListener('beforeunload', function(e) {
                if (self.hasUnsavedChanges()) {
                    e.preventDefault();
                    e.returnValue = 'Masz niezapisane zmiany. Czy na pewno chcesz opuścić stronę?';
                    return e.returnValue;
                }
            });
        },

        /**
         * Handle form submission
         */
        handleFormSubmission: function(event, form) {
            event.preventDefault();
            
            const formId = this.getFormId(form);
            const formData = this.forms[formId];
            
            if (!formData) return;

            // Validate form
            if (!this.validateForm(form)) {
                this.showValidationErrors(form);
                return;
            }

            // Show loading state
            this.setFormLoading(form, true);

            // Prepare form data
            const submitData = this.prepareFormData(form);

            // Submit form
            this.submitForm(form, submitData)
                .then(response => {
                    this.handleSubmissionSuccess(form, response);
                })
                .catch(error => {
                    this.handleSubmissionError(form, error);
                })
                .finally(() => {
                    this.setFormLoading(form, false);
                });
        },

        /**
         * Handle input changes
         */
        handleInputChange: function(event, form) {
            const formId = this.getFormId(form);
            const formData = this.forms[formId];
            
            if (!formData) return;

            formData.isDirty = true;
            
            // Update calculations if needed
            if (this.config.enableCalculations && this.isCalculationField(event.target)) {
                this.updateCalculations(form);
            }

            // Clear field validation errors
            this.clearFieldError(event.target);

            // Update form data
            this.updateFormData(form);
        },

        /**
         * Validate entire form
         */
        validateForm: function(form) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!this.validateField(field, form)) {
                    isValid = false;
                }
            });

            // Custom validation rules
            const customValidations = [
                this.validateInvoiceNumber,
                this.validateDates,
                this.validateAmounts,
                this.validateContractor
            ];

            customValidations.forEach(validation => {
                if (!validation.call(this, form)) {
                    isValid = false;
                }
            });

            return isValid;
        },

        /**
         * Validate individual field
         */
        validateField: function(field, form) {
            if (!field || !this.config.enableValidation) return true;

            let isValid = true;
            const value = field.value.trim();
            
            // Required field validation
            if (field.hasAttribute('required') && !value) {
                this.showFieldError(field, 'To pole jest wymagane');
                isValid = false;
            }

            // Email validation
            if (field.type === 'email' && value && !this.isValidEmail(value)) {
                this.showFieldError(field, 'Nieprawidłowy adres email');
                isValid = false;
            }

            // NIP validation
            if (field.hasAttribute('data-nip') && value && !this.isValidNIP(value)) {
                this.showFieldError(field, 'Nieprawidłowy numer NIP');
                isValid = false;
            }

            // Number validation
            if (field.type === 'number' && value && isNaN(parseFloat(value))) {
                this.showFieldError(field, 'Nieprawidłowa wartość liczbowa');
                isValid = false;
            }

            // Date validation
            if (field.type === 'date' && value && !this.isValidDate(value)) {
                this.showFieldError(field, 'Nieprawidłowa data');
                isValid = false;
            }

            if (isValid) {
                this.clearFieldError(field);
            }

            return isValid;
        },

        /**
         * Validate invoice number
         */
        validateInvoiceNumber: function(form) {
            const numberField = form.querySelector('[name="numer"], [name="invoice_number"]');
            if (!numberField) return true;

            const value = numberField.value.trim();
            if (!value) return true;

            // Check format (basic Polish invoice number format)
            const invoiceNumberPattern = /^[A-Z0-9\/\-]+$/;
            if (!invoiceNumberPattern.test(value)) {
                this.showFieldError(numberField, 'Nieprawidłowy format numeru faktury');
                return false;
            }

            return true;
        },

        /**
         * Validate dates
         */
        validateDates: function(form) {
            const dateFields = form.querySelectorAll('input[type="date"]');
            let isValid = true;

            dateFields.forEach(field => {
                const value = field.value;
                if (value && !this.isValidDate(value)) {
                    this.showFieldError(field, 'Nieprawidłowa data');
                    isValid = false;
                }
            });

            // Check date logic (e.g., due date after issue date)
            const issueDate = form.querySelector('[name="data_wystawienia"], [name="issue_date"]');
            const dueDate = form.querySelector('[name="termin_platnosci"], [name="due_date"]');

            if (issueDate && dueDate && issueDate.value && dueDate.value) {
                if (new Date(dueDate.value) < new Date(issueDate.value)) {
                    this.showFieldError(dueDate, 'Termin płatności nie może być wcześniejszy niż data wystawienia');
                    isValid = false;
                }
            }

            return isValid;
        },

        /**
         * Validate amounts
         */
        validateAmounts: function(form) {
            const amountFields = form.querySelectorAll('[data-amount], .amount-field');
            let isValid = true;

            amountFields.forEach(field => {
                const value = parseFloat(field.value);
                if (field.value && (isNaN(value) || value < 0)) {
                    this.showFieldError(field, 'Kwota musi być liczbą większą lub równą 0');
                    isValid = false;
                }
            });

            return isValid;
        },

        /**
         * Validate contractor information
         */
        validateContractor: function(form) {
            const nipField = form.querySelector('[name="kontrahent_nip"], [name="contractor_nip"]');
            if (nipField && nipField.value) {
                if (!this.isValidNIP(nipField.value)) {
                    this.showFieldError(nipField, 'Nieprawidłowy numer NIP');
                    return false;
                }
            }

            return true;
        },

        /**
         * Update calculations (totals, VAT, etc.)
         */
        updateCalculations: function(form) {
            if (!this.config.enableCalculations) return;

            const items = this.getInvoiceItems(form);
            let subtotal = 0;
            let vatTotal = 0;
            let total = 0;

            items.forEach(item => {
                const quantity = parseFloat(item.quantity) || 0;
                const price = parseFloat(item.price) || 0;
                const vatRate = parseFloat(item.vatRate) || 0;

                const itemTotal = quantity * price;
                const itemVat = itemTotal * (vatRate / 100);

                subtotal += itemTotal;
                vatTotal += itemVat;

                // Update item total display
                if (item.totalField) {
                    item.totalField.value = itemTotal.toFixed(2);
                }
            });

            total = subtotal + vatTotal;

            // Update form totals
            this.updateFormTotals(form, {
                subtotal: subtotal,
                vatTotal: vatTotal,
                total: total
            });
        },

        /**
         * Get invoice items from form
         */
        getInvoiceItems: function(form) {
            const items = [];
            const itemRows = form.querySelectorAll('[data-item-row], .invoice-item');

            itemRows.forEach(row => {
                const quantityField = row.querySelector('[data-quantity], [name*="quantity"]');
                const priceField = row.querySelector('[data-price], [name*="price"]');
                const vatField = row.querySelector('[data-vat], [name*="vat"]');
                const totalField = row.querySelector('[data-total], [name*="total"]');

                if (quantityField && priceField) {
                    items.push({
                        quantity: quantityField.value,
                        price: priceField.value,
                        vatRate: vatField ? vatField.value : 23,
                        totalField: totalField
                    });
                }
            });

            return items;
        },

        /**
         * Update form totals display
         */
        updateFormTotals: function(form, totals) {
            const subtotalField = form.querySelector('[data-subtotal], [name="subtotal"]');
            const vatTotalField = form.querySelector('[data-vat-total], [name="vat_total"]');
            const totalField = form.querySelector('[data-total], [name="total"]');

            if (subtotalField) {
                subtotalField.value = totals.subtotal.toFixed(2);
            }
            if (vatTotalField) {
                vatTotalField.value = totals.vatTotal.toFixed(2);
            }
            if (totalField) {
                totalField.value = totals.total.toFixed(2);
            }

            // Update display elements
            const subtotalDisplay = form.querySelector('.subtotal-display');
            const vatTotalDisplay = form.querySelector('.vat-total-display');
            const totalDisplay = form.querySelector('.total-display');

            if (subtotalDisplay) {
                subtotalDisplay.textContent = totals.subtotal.toFixed(2) + ' zł';
            }
            if (vatTotalDisplay) {
                vatTotalDisplay.textContent = totals.vatTotal.toFixed(2) + ' zł';
            }
            if (totalDisplay) {
                totalDisplay.textContent = totals.total.toFixed(2) + ' zł';
            }
        },

        /**
         * Add invoice item row
         */
        addInvoiceItem: function(button) {
            const form = button.closest('form');
            const itemsContainer = form.querySelector('[data-items-container], .invoice-items');
            
            if (!itemsContainer) return;

            const itemTemplate = this.getItemTemplate(form);
            const itemRow = document.createElement('div');
            itemRow.innerHTML = itemTemplate;
            itemRow.className = 'invoice-item mb-3';
            itemRow.setAttribute('data-item-row', '');

            itemsContainer.appendChild(itemRow);

            // Setup event listeners for new item
            this.setupItemEventListeners(itemRow);

            // Update calculations
            this.updateCalculations(form);
        },

        /**
         * Remove invoice item row
         */
        removeInvoiceItem: function(button) {
            const itemRow = button.closest('[data-item-row], .invoice-item');
            const form = button.closest('form');
            
            if (itemRow) {
                itemRow.remove();
                this.updateCalculations(form);
            }
        },

        /**
         * Get item template HTML
         */
        getItemTemplate: function(form) {
            const existingTemplate = form.querySelector('[data-item-template]');
            if (existingTemplate) {
                return existingTemplate.innerHTML;
            }

            // Default template
            return `
                <div class="row">
                    <div class="col-md-4">
                        <input type="text" class="form-control" name="item_name[]" placeholder="Nazwa towaru/usługi" required>
                    </div>
                    <div class="col-md-2">
                        <input type="number" class="form-control" name="item_quantity[]" data-quantity step="0.01" min="0" placeholder="Ilość" required>
                    </div>
                    <div class="col-md-2">
                        <input type="number" class="form-control" name="item_price[]" data-price step="0.01" min="0" placeholder="Cena" required>
                    </div>
                    <div class="col-md-2">
                        <select class="form-control" name="item_vat[]" data-vat>
                            <option value="23">23%</option>
                            <option value="8">8%</option>
                            <option value="5">5%</option>
                            <option value="0">0%</option>
                        </select>
                    </div>
                    <div class="col-md-1">
                        <input type="number" class="form-control" name="item_total[]" data-total readonly>
                    </div>
                    <div class="col-md-1">
                        <button type="button" class="btn btn-danger btn-sm" data-remove-item>
                            <i class="ri-delete-bin-line"></i>
                        </button>
                    </div>
                </div>
            `;
        },

        /**
         * Setup event listeners for item row
         */
        setupItemEventListeners: function(itemRow) {
            const form = itemRow.closest('form');
            const inputs = itemRow.querySelectorAll('input, select');
            
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    this.updateCalculations(form);
                });
            });
        },

        /**
         * Handle contractor lookup
         */
        handleContractorLookup: function(field) {
            if (!this.config.enableContractorLookup) return;

            const query = field.value.trim();
            if (query.length < 3) return;

            // Debounce the lookup
            clearTimeout(this.contractorLookupTimer);
            this.contractorLookupTimer = setTimeout(() => {
                this.performContractorLookup(field, query);
            }, 500);
        },

        /**
         * Perform contractor lookup
         */
        performContractorLookup: function(field, query) {
            const form = field.closest('form');
            
            fetch('/api/contractors/search/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ query: query })
            })
            .then(response => response.json())
            .then(data => {
                this.showContractorSuggestions(field, data.contractors || []);
            })
            .catch(error => {
                console.error('Contractor lookup failed:', error);
            });
        },

        /**
         * Show contractor suggestions
         */
        showContractorSuggestions: function(field, contractors) {
            // Remove existing suggestions
            const existingSuggestions = document.querySelector('.contractor-suggestions');
            if (existingSuggestions) {
                existingSuggestions.remove();
            }

            if (contractors.length === 0) return;

            // Create suggestions dropdown
            const suggestions = document.createElement('div');
            suggestions.className = 'contractor-suggestions';
            suggestions.style.cssText = `
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                z-index: 1000;
                max-height: 200px;
                overflow-y: auto;
            `;

            contractors.forEach(contractor => {
                const item = document.createElement('div');
                item.className = 'suggestion-item';
                item.style.cssText = 'padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #eee;';
                item.innerHTML = `
                    <div><strong>${contractor.nazwa}</strong></div>
                    <div><small>${contractor.nip} - ${contractor.adres}</small></div>
                `;

                item.addEventListener('click', () => {
                    this.selectContractor(field, contractor);
                    suggestions.remove();
                });

                suggestions.appendChild(item);
            });

            // Position and show suggestions
            field.parentNode.style.position = 'relative';
            field.parentNode.appendChild(suggestions);

            // Close on outside click
            setTimeout(() => {
                document.addEventListener('click', function closeHandler(e) {
                    if (!suggestions.contains(e.target) && e.target !== field) {
                        suggestions.remove();
                        document.removeEventListener('click', closeHandler);
                    }
                });
            }, 100);
        },

        /**
         * Select contractor and fill form fields
         */
        selectContractor: function(field, contractor) {
            const form = field.closest('form');
            
            // Fill contractor fields
            const fields = {
                'kontrahent_nazwa': contractor.nazwa,
                'kontrahent_nip': contractor.nip,
                'kontrahent_adres': contractor.adres,
                'kontrahent_email': contractor.email,
                'kontrahent_telefon': contractor.telefon
            };

            Object.entries(fields).forEach(([name, value]) => {
                const fieldElement = form.querySelector(`[name="${name}"]`);
                if (fieldElement && value) {
                    fieldElement.value = value;
                }
            });
        },

        /**
         * Setup auto-save functionality
         */
        setupAutoSave: function() {
            if (!this.config.enableAutoSave) return;

            const self = this;
            this.autoSaveTimer = setInterval(() => {
                self.performAutoSave();
            }, this.config.autoSaveInterval);
        },

        /**
         * Perform auto-save
         */
        performAutoSave: function() {
            Object.entries(this.forms).forEach(([formId, formData]) => {
                if (formData.isDirty && formData.element) {
                    this.saveFormDraft(formData.element);
                }
            });
        },

        /**
         * Save form as draft
         */
        saveFormDraft: function(form) {
            const formData = this.prepareFormData(form);
            
            fetch('/api/invoices/save-draft/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Draft saved successfully');
                    const formId = this.getFormId(form);
                    if (this.forms[formId]) {
                        this.forms[formId].isDirty = false;
                    }
                }
            })
            .catch(error => {
                console.error('Auto-save failed:', error);
            });
        },

        /**
         * Prepare form data for submission
         */
        prepareFormData: function(form) {
            const formData = new FormData(form);
            const data = {};
            
            for (const [key, value] of formData.entries()) {
                if (data[key]) {
                    if (Array.isArray(data[key])) {
                        data[key].push(value);
                    } else {
                        data[key] = [data[key], value];
                    }
                } else {
                    data[key] = value;
                }
            }
            
            return data;
        },

        /**
         * Submit form data
         */
        submitForm: function(form, data) {
            const action = form.getAttribute('action') || '/api/invoices/create/';
            const method = form.getAttribute('method') || 'POST';
            
            return fetch(action, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            });
        },

        /**
         * Handle successful form submission
         */
        handleSubmissionSuccess: function(form, response) {
            // Clear dirty flag
            const formId = this.getFormId(form);
            if (this.forms[formId]) {
                this.forms[formId].isDirty = false;
            }

            // Show success message
            this.showMessage('Faktura została zapisana pomyślnie', 'success');

            // Redirect if specified
            if (response.redirect_url) {
                window.location.href = response.redirect_url;
            } else if (response.invoice_id) {
                window.location.href = `/faktury/${response.invoice_id}/`;
            }
        },

        /**
         * Handle form submission error
         */
        handleSubmissionError: function(form, error) {
            console.error('Form submission error:', error);
            
            // Show error message
            this.showMessage('Wystąpił błąd podczas zapisywania faktury', 'error');

            // Show field errors if available
            if (error.field_errors) {
                this.showFieldErrors(form, error.field_errors);
            }
        },

        /**
         * Utility methods
         */
        getFormId: function(form) {
            return form.id || Array.from(document.forms).indexOf(form).toString();
        },

        isCalculationField: function(field) {
            return field.hasAttribute('data-quantity') || 
                   field.hasAttribute('data-price') || 
                   field.hasAttribute('data-vat');
        },

        isValidEmail: function(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        },

        isValidNIP: function(nip) {
            const cleanNip = nip.replace(/[-\s]/g, '');
            return /^\d{10}$/.test(cleanNip);
        },

        isValidDate: function(dateString) {
            const date = new Date(dateString);
            return date instanceof Date && !isNaN(date);
        },

        hasUnsavedChanges: function() {
            return Object.values(this.forms).some(form => form.isDirty);
        },

        getCSRFToken: function() {
            const token = document.querySelector('meta[name="csrf-token"]');
            return token ? token.getAttribute('content') : '';
        },

        showFieldError: function(field, message) {
            this.clearFieldError(field);
            
            field.classList.add('is-invalid');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = message;
            field.parentNode.appendChild(errorDiv);
        },

        clearFieldError: function(field) {
            field.classList.remove('is-invalid');
            const errorDiv = field.parentNode.querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.remove();
            }
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
                alert(message);
            }
        },

        setFormLoading: function(form, loading) {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = loading;
                submitBtn.textContent = loading ? 'Zapisywanie...' : 'Zapisz';
            }
        },

        updateFormData: function(form) {
            const formId = this.getFormId(form);
            if (this.forms[formId]) {
                this.forms[formId].data = this.prepareFormData(form);
            }
        }
    };

    // Initialize invoice form manager when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            InvoiceFormManager.init();
        });
    } else {
        InvoiceFormManager.init();
    }

    // Make InvoiceFormManager globally available
    window.InvoiceFormManager = InvoiceFormManager;

})();