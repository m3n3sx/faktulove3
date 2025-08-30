
        // Contextual Help and Tooltip System
        class HelpTooltipSystem {
            constructor() {
                this.helpContent = {
  "invoice_form": {
    "numer_faktury": {
      "title": "Numer faktury",
      "content": "Unikalny numer faktury. Mo\u017ce by\u0107 generowany automatycznie lub wprowadzony r\u0119cznie.",
      "tips": [
        "U\u017cyj automatycznej numeracji dla sp\u00f3jno\u015bci",
        "Format: FV/YYYY/MM/NNN (np. FV/2025/01/001)"
      ]
    },
    "nabywca": {
      "title": "Wyb\u00f3r nabywcy",
      "content": "Wybierz kontrahenta z listy lub dodaj nowego.",
      "tips": [
        "U\u017cyj Ctrl+Shift+N aby szybko doda\u0107 nowego kontrahenta",
        "Wpisz NIP aby automatycznie pobra\u0107 dane z GUS"
      ]
    },
    "pozycje_faktury": {
      "title": "Pozycje faktury",
      "content": "Dodaj produkty lub us\u0142ugi do faktury.",
      "tips": [
        "U\u017cyj Alt+A aby szybko doda\u0107 now\u0105 pozycj\u0119",
        "Wybierz produkt z listy aby automatycznie uzupe\u0142ni\u0107 dane"
      ]
    }
  },
  "ocr_upload": {
    "file_selection": {
      "title": "Wyb\u00f3r pliku",
      "content": "Wybierz plik PDF, JPG, PNG lub TIFF z faktur\u0105 do przetworzenia.",
      "tips": [
        "Przeci\u0105gnij i upu\u015b\u0107 plik na obszar przesy\u0142ania",
        "Najlepsze wyniki dla skan\u00f3w o rozdzielczo\u015bci min. 300 DPI"
      ]
    },
    "processing_results": {
      "title": "Wyniki przetwarzania",
      "content": "Sprawd\u017a i popraw rozpoznane dane przed utworzeniem faktury.",
      "tips": [
        "Zwr\u00f3\u0107 uwag\u0119 na poziom pewno\u015bci rozpoznania",
        "Popraw b\u0142\u0119dnie rozpoznane dane przed zapisem"
      ]
    }
  }
};
                this.init();
            }
            
            init() {
                this.createTooltips();
                this.addHelpButtons();
                this.initializeTooltipBehavior();
            }
            
            createTooltips() {
                // Add help tooltips to form fields
                document.querySelectorAll('input, select, textarea').forEach(field => {
                    const fieldName = field.name || field.id;
                    const context = this.getFieldContext(field);
                    
                    if (this.helpContent[context] && this.helpContent[context][fieldName]) {
                        this.addTooltipToField(field, this.helpContent[context][fieldName]);
                    }
                });
            }
            
            getFieldContext(field) {
                const form = field.closest('form');
                if (!form) return 'general';
                
                if (form.action.includes('fakture')) return 'invoice_form';
                if (form.action.includes('ocr')) return 'ocr_upload';
                
                return 'general';
            }
            
            addTooltipToField(field, helpData) {
                const wrapper = document.createElement('div');
                wrapper.className = 'field-with-help';
                
                // Wrap the field
                field.parentNode.insertBefore(wrapper, field);
                wrapper.appendChild(field);
                
                // Add help button
                const helpButton = document.createElement('button');
                helpButton.type = 'button';
                helpButton.className = 'help-button';
                helpButton.innerHTML = '<iconify-icon icon="heroicons:question-mark-circle"></iconify-icon>';
                helpButton.setAttribute('data-bs-toggle', 'tooltip');
                helpButton.setAttribute('data-bs-placement', 'top');
                helpButton.setAttribute('title', helpData.content);
                
                wrapper.appendChild(helpButton);
                
                // Add detailed help on click
                helpButton.addEventListener('click', () => {
                    this.showDetailedHelp(helpData);
                });
            }
            
            addHelpButtons() {
                // Add help buttons to sections
                document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
                    const sectionId = heading.id || heading.textContent.toLowerCase().replace(/\s+/g, '_');
                    
                    if (this.hasHelpForSection(sectionId)) {
                        const helpButton = document.createElement('button');
                        helpButton.type = 'button';
                        helpButton.className = 'section-help-button';
                        helpButton.innerHTML = '<iconify-icon icon="heroicons:information-circle"></iconify-icon>';
                        helpButton.onclick = () => this.showSectionHelp(sectionId);
                        
                        heading.appendChild(helpButton);
                    }
                });
            }
            
            hasHelpForSection(sectionId) {
                // Check if we have help content for this section
                for (const context of Object.values(this.helpContent)) {
                    if (context[sectionId]) return true;
                }
                return false;
            }
            
            showDetailedHelp(helpData) {
                const modal = this.createHelpModal(helpData);
                document.body.appendChild(modal);
                
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                
                // Remove modal after hiding
                modal.addEventListener('hidden.bs.modal', () => {
                    modal.remove();
                });
            }
            
            createHelpModal(helpData) {
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${helpData.title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>${helpData.content}</p>
                                ${helpData.tips ? this.formatTips(helpData.tips) : ''}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zamknij</button>
                            </div>
                        </div>
                    </div>
                `;
                
                return modal;
            }
            
            formatTips(tips) {
                let html = '<div class="help-tips"><h6>Wskazówki:</h6><ul>';
                tips.forEach(tip => {
                    html += `<li>${tip}</li>`;
                });
                html += '</ul></div>';
                return html;
            }
            
            initializeTooltipBehavior() {
                // Initialize Bootstrap tooltips
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl);
                });
            }
        }
        
        // Initialize help system
        document.addEventListener('DOMContentLoaded', function() {
            window.helpTooltipSystem = new HelpTooltipSystem();
        });
        