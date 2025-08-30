/**
 * Real-time Form Validation for FaktuLove
 * 
 * Provides instant validation feedback with Polish business rules,
 * field highlighting, and correction guidance.
 */

class RealTimeValidator {
    constructor(options = {}) {
        this.options = {
            validateOnInput: true,
            validateOnBlur: true,
            showSuccessMessages: true,
            debounceDelay: 300,
            apiEndpoint: '/api/validate-field/',
            ...options
        };
        
        this.validationCache = new Map();
        this.debounceTimers = new Map();
        this.validatedFields = new Set();
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupStyles();
        this.loadValidationRules();
    }
    
    setupEventListeners() {
        // Listen for input events on form fields
        document.addEventListener('input', (e) => {
            if (this.isValidatableField(e.target)) {
                this.handleFieldInput(e.target);
            }
        });
        
        // Listen for blur events for immediate validation
        document.addEventListener('blur', (e) => {
            if (this.isValidatableField(e.target)) {
                this.handleFieldBlur(e.target);
            }
        }, true);
        
        // Listen for form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.tagName === 'FORM') {
                this.handleFormSubmit(e);
            }
        });
        
        // Listen for paste events
        document.addEventListener('paste', (e) => {
            if (this.isValidatableField(e.target)) {
                setTimeout(() => this.validateField(e.target), 100);
            }
        });
    }
    
    setupStyles() {
        // Add CSS for validation states if not already present
        if (!document.getElementById('real-time-validation-styles')) {
            const style = document.createElement('style');
            style.id = 'real-time-validation-styles';
            style.textContent = `
                .field-valid {
                    border-color: #28a745 !important;
                    box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25) !important;
                }
                
                .field-invalid {
                    border-color: #dc3545 !important;
                    box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
                }
                
                .field-validating {
                    border-color: #ffc107 !important;
                    box-shadow: 0 0 0 0.2rem rgba(255, 193, 7, 0.25) !important;
                }
                
                .validation-message {
                    font-size: 0.875rem;
                    margin-top: 0.25rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .validation-message.success {
                    color: #28a745;
                }
                
                .validation-message.error {
                    color: #dc3545;
                }
                
                .validation-message.info {
                    color: #17a2b8;
                }
                
                .validation-suggestions {
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 0.375rem;
                    padding: 0.75rem;
                    margin-top: 0.5rem;
                    font-size: 0.875rem;
                }
                
                .validation-suggestions h6 {
                    margin: 0 0 0.5rem 0;
                    font-size: 0.875rem;
                    font-weight: 600;
                    color: #495057;
                }
                
                .validation-suggestions ul {
                    margin: 0;
                    padding-left: 1.25rem;
                }
                
                .validation-suggestions li {
                    margin-bottom: 0.25rem;
                    color: #6c757d;
                }
                
                .validation-icon {
                    width: 1rem;
                    height: 1rem;
                    flex-shrink: 0;
                }
                
                .validation-spinner {
                    animation: spin 1s linear infinite;
                }
                
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                
                .field-group {
                    position: relative;
                }
                
                .validation-tooltip {
                    position: absolute;
                    top: 100%;
                    left: 0;
                    right: 0;
                    z-index: 1000;
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 0.375rem;
                    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
                    padding: 0.75rem;
                    margin-top: 0.25rem;
                    font-size: 0.875rem;
                    display: none;
                }
                
                .validation-tooltip.show {
                    display: block;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    loadValidationRules() {
        // Load validation rules from server or define locally
        this.validationRules = {
            nip: {
                required: true,
                pattern: /^\d{10}$/,
                serverValidation: true
            },
            regon: {
                required: false,
                pattern: /^\d{9}$|^\d{14}$/,
                serverValidation: true
            },
            krs: {
                required: false,
                pattern: /^\d{10}$/,
                serverValidation: true
            },
            email: {
                required: true,
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                serverValidation: false
            },
            phone: {
                required: false,
                pattern: /^(\+48\s?)?\d{3}\s?\d{3}\s?\d{3}$/,
                serverValidation: false
            },
            postal_code: {
                required: true,
                pattern: /^\d{2}-\d{3}$/,
                serverValidation: false
            },
            vat_rate: {
                required: true,
                serverValidation: true
            },
            amount: {
                required: true,
                pattern: /^\d+(\.\d{1,2})?$/,
                serverValidation: false
            }
        };
    }
    
    isValidatableField(field) {
        return field && (
            field.tagName === 'INPUT' ||
            field.tagName === 'SELECT' ||
            field.tagName === 'TEXTAREA'
        ) && field.dataset.validate !== 'false';
    }
    
    handleFieldInput(field) {
        if (!this.options.validateOnInput) return;
        
        // Clear existing timer
        if (this.debounceTimers.has(field)) {
            clearTimeout(this.debounceTimers.get(field));
        }
        
        // Set new timer
        const timer = setTimeout(() => {
            this.validateField(field);
            this.debounceTimers.delete(field);
        }, this.options.debounceDelay);
        
        this.debounceTimers.set(field, timer);
    }
    
    handleFieldBlur(field) {
        if (!this.options.validateOnBlur) return;
        
        // Clear debounce timer and validate immediately
        if (this.debounceTimers.has(field)) {
            clearTimeout(this.debounceTimers.get(field));
            this.debounceTimers.delete(field);
        }
        
        this.validateField(field);
    }
    
    async handleFormSubmit(form) {
        const fields = form.querySelectorAll('input, select, textarea');
        const validationPromises = [];
        
        // Validate all fields
        for (const field of fields) {
            if (this.isValidatableField(field)) {
                validationPromises.push(this.validateField(field));
            }
        }
        
        // Wait for all validations to complete
        const results = await Promise.all(validationPromises);
        
        // Check if any validation failed
        const hasErrors = results.some(result => !result.valid);
        
        if (hasErrors) {
            // Prevent form submission
            form.addEventListener('submit', (e) => e.preventDefault(), { once: true });
            
            // Focus on first invalid field
            const firstInvalidField = form.querySelector('.field-invalid');
            if (firstInvalidField) {
                firstInvalidField.focus();
                firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            // Show summary message
            this.showFormValidationSummary(form, results);
        }
    }
    
    async validateField(field) {
        const fieldName = this.getFieldName(field);
        const value = field.value;
        
        // Check cache first
        const cacheKey = `${fieldName}:${value}`;
        if (this.validationCache.has(cacheKey)) {
            const cachedResult = this.validationCache.get(cacheKey);
            this.updateFieldUI(field, cachedResult);
            return cachedResult;
        }
        
        // Show validating state
        this.setFieldState(field, 'validating');
        
        try {
            // Client-side validation first
            const clientResult = this.validateClientSide(fieldName, value);
            
            if (!clientResult.valid) {
                this.updateFieldUI(field, clientResult);
                this.validationCache.set(cacheKey, clientResult);
                return clientResult;
            }
            
            // Server-side validation if needed
            const rule = this.validationRules[fieldName];
            if (rule && rule.serverValidation) {
                const serverResult = await this.validateServerSide(fieldName, value, field);
                this.updateFieldUI(field, serverResult);
                this.validationCache.set(cacheKey, serverResult);
                return serverResult;
            } else {
                this.updateFieldUI(field, clientResult);
                this.validationCache.set(cacheKey, clientResult);
                return clientResult;
            }
            
        } catch (error) {
            console.error('Validation error:', error);
            const errorResult = {
                valid: false,
                error: 'Błąd walidacji',
                suggestions: ['Spróbuj ponownie', 'Sprawdź połączenie internetowe']
            };
            this.updateFieldUI(field, errorResult);
            return errorResult;
        }
    }
    
    validateClientSide(fieldName, value) {
        const rule = this.validationRules[fieldName];
        
        // Check if required
        if (rule && rule.required && (!value || value.trim() === '')) {
            return {
                valid: false,
                error: 'To pole jest wymagane',
                suggestions: ['Wprowadź wartość w tym polu']
            };
        }
        
        // Check pattern if value is provided
        if (value && rule && rule.pattern && !rule.pattern.test(value)) {
            return {
                valid: false,
                error: this.getPatternErrorMessage(fieldName),
                suggestions: this.getPatternSuggestions(fieldName)
            };
        }
        
        // Additional client-side validations
        if (fieldName === 'amount' && value) {
            const amount = parseFloat(value);
            if (isNaN(amount) || amount < 0) {
                return {
                    valid: false,
                    error: 'Kwota musi być liczbą większą lub równą 0',
                    suggestions: ['Wprowadź prawidłową kwotę', 'Użyj kropki jako separatora dziesiętnego']
                };
            }
        }
        
        return {
            valid: true,
            message: 'Pole jest prawidłowe'
        };
    }
    
    async validateServerSide(fieldName, value, field) {
        const context = this.getValidationContext(field);
        
        const response = await fetch(this.options.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                field_name: fieldName,
                value: value,
                context: context
            })
        });
        
        if (!response.ok) {
            throw new Error('Server validation failed');
        }
        
        return await response.json();
    }
    
    updateFieldUI(field, result) {
        // Update field state
        if (result.valid) {
            this.setFieldState(field, 'valid');
        } else {
            this.setFieldState(field, 'invalid');
        }
        
        // Update validation message
        this.updateValidationMessage(field, result);
        
        // Update formatted value if provided
        if (result.formatted_value && result.formatted_value !== field.value) {
            field.value = result.formatted_value;
        }
        
        // Mark field as validated
        this.validatedFields.add(field);
    }
    
    setFieldState(field, state) {
        // Remove existing state classes
        field.classList.remove('field-valid', 'field-invalid', 'field-validating');
        
        // Add new state class
        field.classList.add(`field-${state}`);
        
        // Update aria attributes for accessibility
        if (state === 'valid') {
            field.setAttribute('aria-invalid', 'false');
        } else if (state === 'invalid') {
            field.setAttribute('aria-invalid', 'true');
        }
    }
    
    updateValidationMessage(field, result) {
        const messageId = `validation-message-${field.id || field.name}`;
        let messageElement = document.getElementById(messageId);
        
        // Create message element if it doesn't exist
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.id = messageId;
            messageElement.className = 'validation-message';
            
            // Insert after field or field group
            const fieldGroup = field.closest('.field-group, .form-group, .mb-3');
            if (fieldGroup) {
                fieldGroup.appendChild(messageElement);
            } else {
                field.parentNode.insertBefore(messageElement, field.nextSibling);
            }
        }
        
        // Update message content
        if (result.valid && result.message && this.options.showSuccessMessages) {
            messageElement.className = 'validation-message success';
            messageElement.innerHTML = `
                <i class="fas fa-check-circle validation-icon"></i>
                <span>${result.message}</span>
            `;
        } else if (!result.valid && result.error) {
            messageElement.className = 'validation-message error';
            messageElement.innerHTML = `
                <i class="fas fa-exclamation-circle validation-icon"></i>
                <span>${result.error}</span>
            `;
            
            // Add suggestions if available
            if (result.suggestions && result.suggestions.length > 0) {
                const suggestionsElement = document.createElement('div');
                suggestionsElement.className = 'validation-suggestions';
                suggestionsElement.innerHTML = `
                    <h6><i class="fas fa-lightbulb"></i> Wskazówki:</h6>
                    <ul>
                        ${result.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                `;
                messageElement.appendChild(suggestionsElement);
            }
        } else {
            messageElement.innerHTML = '';
        }
        
        // Update aria-describedby for accessibility
        if (messageElement.textContent.trim()) {
            field.setAttribute('aria-describedby', messageId);
        } else {
            field.removeAttribute('aria-describedby');
        }
    }
    
    showFormValidationSummary(form, results) {
        const errors = results.filter(result => !result.valid);
        
        if (errors.length === 0) return;
        
        // Create or update summary element
        let summaryElement = form.querySelector('.form-validation-summary');
        if (!summaryElement) {
            summaryElement = document.createElement('div');
            summaryElement.className = 'alert alert-danger form-validation-summary';
            form.insertBefore(summaryElement, form.firstChild);
        }
        
        summaryElement.innerHTML = `
            <h6><i class="fas fa-exclamation-triangle"></i> Formularz zawiera błędy:</h6>
            <ul class="mb-0">
                ${errors.map(error => `<li>${error.error}</li>`).join('')}
            </ul>
            <small class="mt-2 d-block">Popraw błędy i spróbuj ponownie.</small>
        `;
        
        // Scroll to summary
        summaryElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    getFieldName(field) {
        return field.dataset.validateAs || field.name || field.id;
    }
    
    getValidationContext(field) {
        const form = field.closest('form');
        const context = {};
        
        // Add form-specific context
        if (form) {
            const firmaField = form.querySelector('[name="firma"], [name="firma_id"]');
            if (firmaField) {
                context.firma_id = firmaField.value;
            }
            
            const checkUniqueness = field.dataset.checkUniqueness === 'true';
            if (checkUniqueness) {
                context.check_uniqueness = true;
            }
        }
        
        return context;
    }
    
    getPatternErrorMessage(fieldName) {
        const messages = {
            nip: 'NIP musi mieć dokładnie 10 cyfr',
            regon: 'REGON musi mieć 9 lub 14 cyfr',
            krs: 'KRS musi mieć dokładnie 10 cyfr',
            email: 'Nieprawidłowy format adresu email',
            phone: 'Nieprawidłowy format numeru telefonu',
            postal_code: 'Kod pocztowy musi mieć format XX-XXX',
            amount: 'Nieprawidłowy format kwoty'
        };
        return messages[fieldName] || 'Nieprawidłowy format';
    }
    
    getPatternSuggestions(fieldName) {
        const suggestions = {
            nip: ['Wprowadź 10 cyfr bez spacji i myślników', 'Przykład: 1234567890'],
            regon: ['Wprowadź 9 lub 14 cyfr', 'Usuń spacje i myślniki'],
            krs: ['Wprowadź 10 cyfr', 'Przykład: 0000123456'],
            email: ['Użyj formatu: nazwa@domena.pl', 'Sprawdź czy adres zawiera znak @'],
            phone: ['Użyj formatu: +48 123 456 789', 'Lub: 123 456 789'],
            postal_code: ['Użyj formatu: XX-XXX', 'Przykład: 00-001'],
            amount: ['Użyj kropki jako separatora dziesiętnego', 'Przykład: 123.45']
        };
        return suggestions[fieldName] || ['Sprawdź format danych'];
    }
    
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
    
    // Public methods
    validateForm(form) {
        return this.handleFormSubmit(form);
    }
    
    clearValidation(field) {
        this.setFieldState(field, '');
        const messageId = `validation-message-${field.id || field.name}`;
        const messageElement = document.getElementById(messageId);
        if (messageElement) {
            messageElement.innerHTML = '';
        }
        this.validatedFields.delete(field);
    }
    
    clearCache() {
        this.validationCache.clear();
    }
    
    destroy() {
        // Clear all timers
        for (const timer of this.debounceTimers.values()) {
            clearTimeout(timer);
        }
        this.debounceTimers.clear();
        
        // Clear cache
        this.validationCache.clear();
        
        // Remove event listeners would require storing references
        // For now, just clear internal state
        this.validatedFields.clear();
    }
}

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize real-time validation for forms with data-validate="true"
    const forms = document.querySelectorAll('form[data-validate="true"]');
    
    if (forms.length > 0) {
        window.realTimeValidator = new RealTimeValidator({
            validateOnInput: true,
            validateOnBlur: true,
            showSuccessMessages: true,
            debounceDelay: 300
        });
    }
});

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealTimeValidator;
}