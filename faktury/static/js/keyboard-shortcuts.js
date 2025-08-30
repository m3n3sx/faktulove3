
        // Keyboard Shortcuts Manager for FaktuLove
        class KeyboardShortcutsManager {
            constructor() {
                this.shortcuts = {
  "global": {
    "ctrl+n": {
      "action": "create_new_invoice",
      "description": "Utw\u00f3rz now\u0105 faktur\u0119",
      "url": "dodaj_fakture"
    },
    "ctrl+shift+n": {
      "action": "create_new_contractor",
      "description": "Dodaj nowego kontrahenta",
      "url": "dodaj_kontrahenta"
    },
    "ctrl+u": {
      "action": "ocr_upload",
      "description": "Przejd\u017a do OCR",
      "url": "ocr_upload"
    },
    "ctrl+h": {
      "action": "go_home",
      "description": "Przejd\u017a do panelu g\u0142\u00f3wnego",
      "url": "panel_uzytkownika"
    },
    "ctrl+/": {
      "action": "show_help",
      "description": "Poka\u017c pomoc",
      "function": "showHelpModal()"
    },
    "esc": {
      "action": "close_modal",
      "description": "Zamknij modal",
      "function": "closeActiveModal()"
    }
  },
  "invoice_form": {
    "ctrl+s": {
      "action": "save_invoice",
      "description": "Zapisz faktur\u0119",
      "function": "saveInvoiceForm()"
    },
    "ctrl+shift+s": {
      "action": "save_and_new",
      "description": "Zapisz i utw\u00f3rz now\u0105",
      "function": "saveAndCreateNew()"
    },
    "ctrl+d": {
      "action": "duplicate_invoice",
      "description": "Duplikuj faktur\u0119",
      "function": "duplicateInvoice()"
    },
    "alt+a": {
      "action": "add_invoice_item",
      "description": "Dodaj pozycj\u0119",
      "function": "addInvoiceItem()"
    }
  },
  "invoice_list": {
    "ctrl+f": {
      "action": "focus_search",
      "description": "Szukaj faktur",
      "function": "focusSearchInput()"
    },
    "ctrl+e": {
      "action": "export_invoices",
      "description": "Eksportuj faktury",
      "function": "exportInvoices()"
    }
  }
};
                this.init();
            }
            
            init() {
                document.addEventListener('keydown', (e) => this.handleKeydown(e));
                this.createShortcutsHelp();
            }
            
            handleKeydown(e) {
                const key = this.getKeyString(e);
                const context = this.getCurrentContext();
                
                // Check context-specific shortcuts first
                if (this.shortcuts[context] && this.shortcuts[context][key]) {
                    e.preventDefault();
                    this.executeShortcut(this.shortcuts[context][key]);
                    return;
                }
                
                // Check global shortcuts
                if (this.shortcuts.global[key]) {
                    e.preventDefault();
                    this.executeShortcut(this.shortcuts.global[key]);
                }
            }
            
            getKeyString(e) {
                let key = '';
                
                if (e.ctrlKey) key += 'ctrl+';
                if (e.shiftKey) key += 'shift+';
                if (e.altKey) key += 'alt+';
                
                if (e.key === 'Escape') {
                    key += 'esc';
                } else if (e.key === '/') {
                    key += '/';
                } else {
                    key += e.key.toLowerCase();
                }
                
                return key;
            }
            
            getCurrentContext() {
                // Determine current page context
                if (document.querySelector('form[action*="fakture"]')) {
                    return 'invoice_form';
                } else if (window.location.pathname.includes('faktury')) {
                    return 'invoice_list';
                }
                return 'global';
            }
            
            executeShortcut(shortcut) {
                if (shortcut.url) {
                    window.location.href = '/' + shortcut.url + '/';
                } else if (shortcut.function) {
                    try {
                        eval(shortcut.function);
                    } catch (error) {
                        console.warn('Shortcut function not available:', shortcut.function);
                    }
                }
            }
            
            createShortcutsHelp() {
                // Create shortcuts help modal
                const helpModal = document.createElement('div');
                helpModal.id = 'shortcuts-help-modal';
                helpModal.className = 'modal fade';
                helpModal.innerHTML = `
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Skróty klawiszowe</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                ${this.generateShortcutsHelpContent()}
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(helpModal);
            }
            
            generateShortcutsHelpContent() {
                let content = '';
                
                for (const [context, shortcuts] of Object.entries(this.shortcuts)) {
                    content += `<h6>${this.getContextTitle(context)}</h6>`;
                    content += '<div class="row mb-3">';
                    
                    for (const [key, shortcut] of Object.entries(shortcuts)) {
                        content += `
                            <div class="col-md-6 mb-2">
                                <div class="d-flex justify-content-between">
                                    <span class="shortcut-key">${this.formatKey(key)}</span>
                                    <span class="shortcut-desc">${shortcut.description}</span>
                                </div>
                            </div>
                        `;
                    }
                    
                    content += '</div>';
                }
                
                return content;
            }
            
            getContextTitle(context) {
                const titles = {
                    'global': 'Globalne',
                    'invoice_form': 'Formularz faktury',
                    'invoice_list': 'Lista faktur'
                };
                return titles[context] || context;
            }
            
            formatKey(key) {
                return key.replace('ctrl+', 'Ctrl+')
                         .replace('shift+', 'Shift+')
                         .replace('alt+', 'Alt+')
                         .replace('esc', 'Esc');
            }
        }
        
        // Global shortcut functions
        function showHelpModal() {
            const modal = document.getElementById('shortcuts-help-modal');
            if (modal) {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        }
        
        function closeActiveModal() {
            const activeModal = document.querySelector('.modal.show');
            if (activeModal) {
                const bsModal = bootstrap.Modal.getInstance(activeModal);
                if (bsModal) bsModal.hide();
            }
        }
        
        function toggleQuickActions() {
            const actions = document.getElementById('fabActions');
            if (actions) {
                actions.style.display = actions.style.display === 'none' ? 'flex' : 'none';
            }
        }
        
        function saveInvoiceForm() {
            const form = document.querySelector('form[action*="fakture"]');
            if (form) {
                form.submit();
            }
        }
        
        function saveAndCreateNew() {
            const form = document.querySelector('form[action*="fakture"]');
            if (form) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'save_and_new';
                input.value = '1';
                form.appendChild(input);
                form.submit();
            }
        }
        
        function addInvoiceItem() {
            const addButton = document.getElementById('add-pozycja');
            if (addButton) {
                addButton.click();
            }
        }
        
        function focusSearchInput() {
            const searchInput = document.querySelector('input[name="search"], input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Initialize shortcuts when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            window.keyboardShortcuts = new KeyboardShortcutsManager();
        });
        