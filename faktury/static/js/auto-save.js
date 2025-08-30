
        // Auto-save functionality for FaktuLove forms
        class AutoSaveManager {
            constructor() {
                this.saveInterval = 30000; // 30 seconds
                this.forms = new Map();
                this.init();
            }
            
            init() {
                // Find forms that should have auto-save
                document.querySelectorAll('form[data-auto-save="true"], form.auto-save').forEach(form => {
                    this.enableAutoSave(form);
                });
                
                // Auto-detect invoice and contractor forms
                const invoiceForm = document.querySelector('form[action*="fakture"]');
                const contractorForm = document.querySelector('form[action*="kontrahent"]');
                
                if (invoiceForm) this.enableAutoSave(invoiceForm);
                if (contractorForm) this.enableAutoSave(contractorForm);
            }
            
            enableAutoSave(form) {
                const formId = form.id || 'form_' + Date.now();
                form.id = formId;
                
                const autoSaveData = {
                    form: form,
                    lastSave: Date.now(),
                    isDirty: false,
                    interval: null
                };
                
                this.forms.set(formId, autoSaveData);
                
                // Listen for form changes
                form.addEventListener('input', () => {
                    autoSaveData.isDirty = true;
                    this.showAutoSaveIndicator(formId, 'unsaved');
                });
                
                form.addEventListener('change', () => {
                    autoSaveData.isDirty = true;
                    this.showAutoSaveIndicator(formId, 'unsaved');
                });
                
                // Start auto-save interval
                autoSaveData.interval = setInterval(() => {
                    this.performAutoSave(formId);
                }, this.saveInterval);
                
                // Add auto-save indicator
                this.addAutoSaveIndicator(form);
                
                // Save on page unload
                window.addEventListener('beforeunload', () => {
                    this.saveFormData(formId);
                });
            }
            
            addAutoSaveIndicator(form) {
                const indicator = document.createElement('div');
                indicator.className = 'auto-save-indicator';
                indicator.id = form.id + '_indicator';
                indicator.innerHTML = `
                    <iconify-icon icon="heroicons:cloud-arrow-up"></iconify-icon>
                    <span class="indicator-text">Automatyczne zapisywanie</span>
                `;
                
                // Insert indicator at the top of the form
                form.insertBefore(indicator, form.firstChild);
            }
            
            showAutoSaveIndicator(formId, status) {
                const indicator = document.getElementById(formId + '_indicator');
                if (!indicator) return;
                
                const iconElement = indicator.querySelector('iconify-icon');
                const textElement = indicator.querySelector('.indicator-text');
                
                indicator.className = `auto-save-indicator ${status}`;
                
                switch (status) {
                    case 'saving':
                        iconElement.setAttribute('icon', 'heroicons:arrow-path');
                        textElement.textContent = 'Zapisywanie...';
                        break;
                    case 'saved':
                        iconElement.setAttribute('icon', 'heroicons:check-circle');
                        textElement.textContent = 'Zapisano automatycznie';
                        break;
                    case 'unsaved':
                        iconElement.setAttribute('icon', 'heroicons:exclamation-triangle');
                        textElement.textContent = 'Niezapisane zmiany';
                        break;
                    case 'error':
                        iconElement.setAttribute('icon', 'heroicons:x-circle');
                        textElement.textContent = 'Błąd zapisywania';
                        break;
                }
            }
            
            performAutoSave(formId) {
                const autoSaveData = this.forms.get(formId);
                if (!autoSaveData || !autoSaveData.isDirty) return;
                
                this.showAutoSaveIndicator(formId, 'saving');
                
                try {
                    this.saveFormData(formId);
                    autoSaveData.isDirty = false;
                    autoSaveData.lastSave = Date.now();
                    this.showAutoSaveIndicator(formId, 'saved');
                    
                    // Hide saved indicator after 3 seconds
                    setTimeout(() => {
                        this.showAutoSaveIndicator(formId, 'unsaved');
                    }, 3000);
                    
                } catch (error) {
                    console.error('Auto-save failed:', error);
                    this.showAutoSaveIndicator(formId, 'error');
                }
            }
            
            saveFormData(formId) {
                const autoSaveData = this.forms.get(formId);
                if (!autoSaveData) return;
                
                const form = autoSaveData.form;
                const formData = new FormData(form);
                const data = {};
                
                // Convert FormData to object
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                
                // Save to localStorage
                const storageKey = `autosave_${formId}`;
                localStorage.setItem(storageKey, JSON.stringify({
                    data: data,
                    timestamp: Date.now(),
                    url: window.location.pathname
                }));
            }
            
            restoreFormData(formId) {
                const storageKey = `autosave_${formId}`;
                const savedData = localStorage.getItem(storageKey);
                
                if (!savedData) return false;
                
                try {
                    const parsed = JSON.parse(savedData);
                    
                    // Check if data is recent (within 24 hours)
                    if (Date.now() - parsed.timestamp > 24 * 60 * 60 * 1000) {
                        localStorage.removeItem(storageKey);
                        return false;
                    }
                    
                    // Check if it's the same URL
                    if (parsed.url !== window.location.pathname) {
                        return false;
                    }
                    
                    // Restore form data
                    const form = document.getElementById(formId);
                    if (form) {
                        for (let [key, value] of Object.entries(parsed.data)) {
                            const field = form.querySelector(`[name="${key}"]`);
                            if (field) {
                                field.value = value;
                            }
                        }
                        
                        // Show restore notification
                        this.showRestoreNotification(formId);
                        return true;
                    }
                    
                } catch (error) {
                    console.error('Failed to restore form data:', error);
                    localStorage.removeItem(storageKey);
                }
                
                return false;
            }
            
            showRestoreNotification(formId) {
                const notification = document.createElement('div');
                notification.className = 'alert alert-info alert-dismissible fade show';
                notification.innerHTML = `
                    <iconify-icon icon="heroicons:information-circle"></iconify-icon>
                    Przywrócono automatycznie zapisane dane z poprzedniej sesji.
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                
                const form = document.getElementById(formId);
                form.insertBefore(notification, form.firstChild);
                
                // Auto-hide after 5 seconds
                setTimeout(() => {
                    notification.remove();
                }, 5000);
            }
            
            clearAutoSaveData(formId) {
                const storageKey = `autosave_${formId}`;
                localStorage.removeItem(storageKey);
            }
        }
        
        // Initialize auto-save when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            window.autoSaveManager = new AutoSaveManager();
            
            // Try to restore data for existing forms
            document.querySelectorAll('form[id]').forEach(form => {
                if (window.autoSaveManager.forms.has(form.id)) {
                    window.autoSaveManager.restoreFormData(form.id);
                }
            });
        });
        