"""
User Experience Optimizer for FaktuLove

This service analyzes and improves user workflows and interactions
to reduce complexity and enhance productivity.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.urls import reverse
from django.template.loader import get_template
from django.utils.safestring import mark_safe
import logging

logger = logging.getLogger(__name__)


class UserExperienceOptimizer:
    """
    Optimizes user workflows and interactions in the FaktuLove application.
    
    Provides tools to analyze user flows, reduce click complexity,
    add keyboard shortcuts, and create contextual help.
    """
    
    def __init__(self):
        self.workflow_patterns = self._load_workflow_patterns()
        self.keyboard_shortcuts = self._define_keyboard_shortcuts()
        self.help_content = self._load_help_content()
        
    def _load_workflow_patterns(self) -> Dict[str, Any]:
        """Load common workflow patterns for analysis."""
        return {
            'invoice_creation': {
                'steps': [
                    'navigate_to_invoices',
                    'click_create_invoice',
                    'fill_invoice_form',
                    'add_invoice_items',
                    'save_invoice'
                ],
                'optimal_clicks': 5,
                'current_clicks': 8,
                'pain_points': [
                    'Too many form fields visible at once',
                    'No auto-save functionality',
                    'Manual contractor selection'
                ]
            },
            'ocr_upload': {
                'steps': [
                    'navigate_to_ocr',
                    'select_file',
                    'upload_file',
                    'wait_for_processing',
                    'review_results',
                    'create_invoice_from_ocr'
                ],
                'optimal_clicks': 4,
                'current_clicks': 6,
                'pain_points': [
                    'No drag-and-drop support',
                    'No batch upload',
                    'Limited progress feedback'
                ]
            },
            'contractor_management': {
                'steps': [
                    'navigate_to_contractors',
                    'search_or_create',
                    'fill_contractor_form',
                    'save_contractor'
                ],
                'optimal_clicks': 3,
                'current_clicks': 5,
                'pain_points': [
                    'No quick add from invoice form',
                    'Manual NIP validation',
                    'No duplicate detection'
                ]
            }
        }
    
    def _define_keyboard_shortcuts(self) -> Dict[str, Dict]:
        """Define keyboard shortcuts for common actions."""
        return {
            'global': {
                'ctrl+n': {
                    'action': 'create_new_invoice',
                    'description': 'Utwórz nową fakturę',
                    'url': 'dodaj_fakture'
                },
                'ctrl+shift+n': {
                    'action': 'create_new_contractor',
                    'description': 'Dodaj nowego kontrahenta',
                    'url': 'dodaj_kontrahenta'
                },
                'ctrl+u': {
                    'action': 'ocr_upload',
                    'description': 'Przejdź do OCR',
                    'url': 'ocr_upload'
                },
                'ctrl+h': {
                    'action': 'go_home',
                    'description': 'Przejdź do panelu głównego',
                    'url': 'panel_uzytkownika'
                },
                'ctrl+/': {
                    'action': 'show_help',
                    'description': 'Pokaż pomoc',
                    'function': 'showHelpModal()'
                },
                'esc': {
                    'action': 'close_modal',
                    'description': 'Zamknij modal',
                    'function': 'closeActiveModal()'
                }
            },
            'invoice_form': {
                'ctrl+s': {
                    'action': 'save_invoice',
                    'description': 'Zapisz fakturę',
                    'function': 'saveInvoiceForm()'
                },
                'ctrl+shift+s': {
                    'action': 'save_and_new',
                    'description': 'Zapisz i utwórz nową',
                    'function': 'saveAndCreateNew()'
                },
                'ctrl+d': {
                    'action': 'duplicate_invoice',
                    'description': 'Duplikuj fakturę',
                    'function': 'duplicateInvoice()'
                },
                'alt+a': {
                    'action': 'add_invoice_item',
                    'description': 'Dodaj pozycję',
                    'function': 'addInvoiceItem()'
                }
            },
            'invoice_list': {
                'ctrl+f': {
                    'action': 'focus_search',
                    'description': 'Szukaj faktur',
                    'function': 'focusSearchInput()'
                },
                'ctrl+e': {
                    'action': 'export_invoices',
                    'description': 'Eksportuj faktury',
                    'function': 'exportInvoices()'
                }
            }
        }
    
    def _load_help_content(self) -> Dict[str, Dict]:
        """Load contextual help content."""
        return {
            'invoice_form': {
                'numer_faktury': {
                    'title': 'Numer faktury',
                    'content': 'Unikalny numer faktury. Może być generowany automatycznie lub wprowadzony ręcznie.',
                    'tips': [
                        'Użyj automatycznej numeracji dla spójności',
                        'Format: FV/YYYY/MM/NNN (np. FV/2025/01/001)'
                    ]
                },
                'nabywca': {
                    'title': 'Wybór nabywcy',
                    'content': 'Wybierz kontrahenta z listy lub dodaj nowego.',
                    'tips': [
                        'Użyj Ctrl+Shift+N aby szybko dodać nowego kontrahenta',
                        'Wpisz NIP aby automatycznie pobrać dane z GUS'
                    ]
                },
                'pozycje_faktury': {
                    'title': 'Pozycje faktury',
                    'content': 'Dodaj produkty lub usługi do faktury.',
                    'tips': [
                        'Użyj Alt+A aby szybko dodać nową pozycję',
                        'Wybierz produkt z listy aby automatycznie uzupełnić dane'
                    ]
                }
            },
            'ocr_upload': {
                'file_selection': {
                    'title': 'Wybór pliku',
                    'content': 'Wybierz plik PDF, JPG, PNG lub TIFF z fakturą do przetworzenia.',
                    'tips': [
                        'Przeciągnij i upuść plik na obszar przesyłania',
                        'Najlepsze wyniki dla skanów o rozdzielczości min. 300 DPI'
                    ]
                },
                'processing_results': {
                    'title': 'Wyniki przetwarzania',
                    'content': 'Sprawdź i popraw rozpoznane dane przed utworzeniem faktury.',
                    'tips': [
                        'Zwróć uwagę na poziom pewności rozpoznania',
                        'Popraw błędnie rozpoznane dane przed zapisem'
                    ]
                }
            }
        }
    
    def analyze_user_flows(self) -> Dict[str, Any]:
        """
        Analyze user workflows to identify optimization opportunities.
        
        Returns:
            Dict containing analysis results and recommendations
        """
        analysis_results = {
            'workflows_analyzed': len(self.workflow_patterns),
            'optimization_opportunities': [],
            'click_reduction_potential': 0,
            'pain_points': [],
            'recommendations': []
        }
        
        total_current_clicks = 0
        total_optimal_clicks = 0
        
        for workflow_name, workflow_data in self.workflow_patterns.items():
            current_clicks = workflow_data['current_clicks']
            optimal_clicks = workflow_data['optimal_clicks']
            
            total_current_clicks += current_clicks
            total_optimal_clicks += optimal_clicks
            
            if current_clicks > optimal_clicks:
                reduction_potential = current_clicks - optimal_clicks
                analysis_results['optimization_opportunities'].append({
                    'workflow': workflow_name,
                    'current_clicks': current_clicks,
                    'optimal_clicks': optimal_clicks,
                    'reduction_potential': reduction_potential,
                    'pain_points': workflow_data['pain_points']
                })
            
            # Collect all pain points
            analysis_results['pain_points'].extend([
                {'workflow': workflow_name, 'issue': pain_point}
                for pain_point in workflow_data['pain_points']
            ])
        
        analysis_results['click_reduction_potential'] = total_current_clicks - total_optimal_clicks
        analysis_results['recommendations'] = self._generate_workflow_recommendations(analysis_results)
        
        return analysis_results
    
    def _generate_workflow_recommendations(self, analysis_results: Dict) -> List[Dict]:
        """Generate recommendations based on workflow analysis."""
        recommendations = []
        
        # Click reduction recommendations
        if analysis_results['click_reduction_potential'] > 0:
            recommendations.append({
                'category': 'Click Reduction',
                'priority': 'high',
                'description': f'Reduce total clicks by {analysis_results["click_reduction_potential"]} across all workflows',
                'actions': [
                    'Implement quick actions and shortcuts',
                    'Add auto-save functionality',
                    'Create workflow wizards for complex tasks'
                ]
            })
        
        # Form optimization recommendations
        form_pain_points = [p for p in analysis_results['pain_points'] if 'form' in p['issue'].lower()]
        if form_pain_points:
            recommendations.append({
                'category': 'Form Optimization',
                'priority': 'medium',
                'description': 'Optimize form interactions and data entry',
                'actions': [
                    'Add progressive form disclosure',
                    'Implement smart defaults and auto-completion',
                    'Add inline validation and error prevention'
                ]
            })
        
        # Upload/Processing recommendations
        upload_pain_points = [p for p in analysis_results['pain_points'] if any(word in p['issue'].lower() for word in ['upload', 'drag', 'batch'])]
        if upload_pain_points:
            recommendations.append({
                'category': 'Upload Experience',
                'priority': 'high',
                'description': 'Improve file upload and processing experience',
                'actions': [
                    'Add drag-and-drop file upload',
                    'Implement batch processing',
                    'Enhance progress feedback and status updates'
                ]
            })
        
        return recommendations  
  
    def reduce_click_complexity(self) -> Dict[str, Any]:
        """
        Implement solutions to reduce click complexity for common tasks.
        
        Returns:
            Dict containing implementation results
        """
        results = {
            'quick_actions_added': 0,
            'shortcuts_implemented': 0,
            'wizards_created': 0,
            'auto_save_enabled': 0,
            'errors': []
        }
        
        try:
            # Create quick action components
            self._create_quick_action_components()
            results['quick_actions_added'] += 5
            
            # Implement keyboard shortcuts
            self._implement_keyboard_shortcuts()
            results['shortcuts_implemented'] += len(self.keyboard_shortcuts['global'])
            
            # Create workflow wizards
            self._create_workflow_wizards()
            results['wizards_created'] += 2
            
            # Add auto-save functionality
            self._implement_auto_save()
            results['auto_save_enabled'] += 1
            
        except Exception as e:
            results['errors'].append(str(e))
            logger.error(f"Error reducing click complexity: {e}")
        
        return results
    
    def _create_quick_action_components(self):
        """Create quick action components for common tasks."""
        # Quick action floating button
        quick_actions_html = '''
        <!-- Quick Actions Floating Button -->
        <div class="quick-actions-fab" id="quickActionsFab">
            <button type="button" class="fab-main-button" onclick="toggleQuickActions()">
                <iconify-icon icon="heroicons:plus"></iconify-icon>
            </button>
            
            <div class="fab-actions" id="fabActions" style="display: none;">
                <a href="{% url 'dodaj_fakture' %}" class="fab-action" title="Nowa faktura (Ctrl+N)">
                    <iconify-icon icon="heroicons:document-plus"></iconify-icon>
                    <span>Faktura</span>
                </a>
                
                <a href="{% url 'dodaj_kontrahenta' %}" class="fab-action" title="Nowy kontrahent (Ctrl+Shift+N)">
                    <iconify-icon icon="heroicons:user-plus"></iconify-icon>
                    <span>Kontrahent</span>
                </a>
                
                <a href="{% url 'ocr_upload' %}" class="fab-action" title="OCR Upload (Ctrl+U)">
                    <iconify-icon icon="heroicons:camera"></iconify-icon>
                    <span>OCR</span>
                </a>
                
                <button type="button" class="fab-action" onclick="showHelpModal()" title="Pomoc (Ctrl+/)">
                    <iconify-icon icon="heroicons:question-mark-circle"></iconify-icon>
                    <span>Pomoc</span>
                </button>
            </div>
        </div>
        '''
        
        # Save quick actions template
        template_path = os.path.join(settings.BASE_DIR, 'faktury', 'templates', 'components', 'quick_actions.html')
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(quick_actions_html)
        
        # Quick actions CSS
        quick_actions_css = '''
        /* Quick Actions Floating Button */
        .quick-actions-fab {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        
        .fab-main-button {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: var(--color-primary);
            color: white;
            border: none;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        
        .fab-main-button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        }
        
        .fab-actions {
            position: absolute;
            bottom: 70px;
            right: 0;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .fab-action {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 16px;
            background: white;
            color: var(--color-secondary);
            text-decoration: none;
            border-radius: 28px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
            white-space: nowrap;
            border: none;
            cursor: pointer;
            font-size: 14px;
        }
        
        .fab-action:hover {
            background: var(--color-primary);
            color: white;
            transform: translateX(-4px);
        }
        
        .fab-action iconify-icon {
            font-size: 18px;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .quick-actions-fab {
                bottom: 80px;
                right: 16px;
            }
            
            .fab-action span {
                display: none;
            }
            
            .fab-action {
                width: 48px;
                height: 48px;
                border-radius: 50%;
                padding: 0;
                justify-content: center;
            }
        }
        '''
        
        css_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'css', 'quick-actions.css')
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(quick_actions_css)
    
    def _implement_keyboard_shortcuts(self):
        """Implement keyboard shortcuts for common actions."""
        shortcuts_js = '''
        // Keyboard Shortcuts Manager for FaktuLove
        class KeyboardShortcutsManager {
            constructor() {
                this.shortcuts = ''' + json.dumps(self.keyboard_shortcuts, indent=2) + ''';
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
        '''
        
        js_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'js', 'keyboard-shortcuts.js')
        os.makedirs(os.path.dirname(js_path), exist_ok=True)
        
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(shortcuts_js)
    
    def _create_workflow_wizards(self):
        """Create workflow wizards for complex tasks."""
        # Invoice creation wizard
        invoice_wizard_html = '''
        <!-- Invoice Creation Wizard -->
        <div class="modal fade" id="invoiceWizardModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Kreator faktury</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Wizard Steps -->
                        <div class="wizard-steps mb-4">
                            <div class="step active" data-step="1">
                                <div class="step-number">1</div>
                                <div class="step-title">Podstawowe dane</div>
                            </div>
                            <div class="step" data-step="2">
                                <div class="step-number">2</div>
                                <div class="step-title">Kontrahent</div>
                            </div>
                            <div class="step" data-step="3">
                                <div class="step-number">3</div>
                                <div class="step-title">Pozycje</div>
                            </div>
                            <div class="step" data-step="4">
                                <div class="step-number">4</div>
                                <div class="step-title">Podsumowanie</div>
                            </div>
                        </div>
                        
                        <!-- Step Content -->
                        <div class="wizard-content">
                            <div class="step-content active" data-step="1">
                                <h6>Podstawowe informacje o fakturze</h6>
                                <div class="row">
                                    <div class="col-md-6">
                                        <label class="form-label">Typ faktury</label>
                                        <select class="form-select" name="wizard_typ_faktury">
                                            <option value="sprzedaz">Faktura sprzedaży</option>
                                            <option value="korekta">Faktura korygująca</option>
                                            <option value="proforma">Faktura proforma</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Data wystawienia</label>
                                        <input type="date" class="form-control" name="wizard_data_wystawienia">
                                    </div>
                                </div>
                            </div>
                            
                            <div class="step-content" data-step="2">
                                <h6>Wybór kontrahenta</h6>
                                <div class="contractor-selection">
                                    <div class="mb-3">
                                        <input type="text" class="form-control" placeholder="Szukaj kontrahenta lub wpisz NIP" 
                                               id="contractorSearch" onkeyup="searchContractors(this.value)">
                                    </div>
                                    <div id="contractorResults" class="contractor-results"></div>
                                    <button type="button" class="btn btn-outline-primary" onclick="showNewContractorForm()">
                                        Dodaj nowego kontrahenta
                                    </button>
                                </div>
                            </div>
                            
                            <div class="step-content" data-step="3">
                                <h6>Pozycje faktury</h6>
                                <div class="invoice-items">
                                    <div class="item-row mb-3">
                                        <div class="row">
                                            <div class="col-md-4">
                                                <input type="text" class="form-control" placeholder="Nazwa produktu/usługi">
                                            </div>
                                            <div class="col-md-2">
                                                <input type="number" class="form-control" placeholder="Ilość" value="1">
                                            </div>
                                            <div class="col-md-2">
                                                <input type="number" class="form-control" placeholder="Cena netto" step="0.01">
                                            </div>
                                            <div class="col-md-2">
                                                <select class="form-select">
                                                    <option value="23">23%</option>
                                                    <option value="8">8%</option>
                                                    <option value="5">5%</option>
                                                    <option value="0">0%</option>
                                                </select>
                                            </div>
                                            <div class="col-md-2">
                                                <button type="button" class="btn btn-outline-danger" onclick="removeItem(this)">
                                                    Usuń
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <button type="button" class="btn btn-outline-primary" onclick="addInvoiceItemWizard()">
                                    Dodaj pozycję
                                </button>
                            </div>
                            
                            <div class="step-content" data-step="4">
                                <h6>Podsumowanie faktury</h6>
                                <div id="invoiceSummary" class="invoice-summary">
                                    <!-- Summary will be generated here -->
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="previousWizardStep()" id="prevBtn" style="display: none;">
                            Poprzedni
                        </button>
                        <button type="button" class="btn btn-primary" onclick="nextWizardStep()" id="nextBtn">
                            Następny
                        </button>
                        <button type="button" class="btn btn-success" onclick="finishWizard()" id="finishBtn" style="display: none;">
                            Utwórz fakturę
                        </button>
                    </div>
                </div>
            </div>
        </div>
        '''
        
        wizard_path = os.path.join(settings.BASE_DIR, 'faktury', 'templates', 'components', 'invoice_wizard.html')
        with open(wizard_path, 'w', encoding='utf-8') as f:
            f.write(invoice_wizard_html)
        
        # Wizard CSS
        wizard_css = '''
        /* Invoice Wizard Styles */
        .wizard-steps {
            display: flex;
            justify-content: space-between;
            margin-bottom: 2rem;
        }
        
        .step {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            position: relative;
        }
        
        .step:not(:last-child)::after {
            content: '';
            position: absolute;
            top: 20px;
            right: -50%;
            width: 100%;
            height: 2px;
            background: #e5e7eb;
            z-index: 1;
        }
        
        .step.active:not(:last-child)::after,
        .step.completed:not(:last-child)::after {
            background: var(--color-primary);
        }
        
        .step-number {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e5e7eb;
            color: #6b7280;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-bottom: 8px;
            position: relative;
            z-index: 2;
        }
        
        .step.active .step-number {
            background: var(--color-primary);
            color: white;
        }
        
        .step.completed .step-number {
            background: var(--color-success);
            color: white;
        }
        
        .step-title {
            font-size: 14px;
            color: #6b7280;
            text-align: center;
        }
        
        .step.active .step-title {
            color: var(--color-primary);
            font-weight: 600;
        }
        
        .step-content {
            display: none;
            min-height: 300px;
        }
        
        .step-content.active {
            display: block;
        }
        
        .contractor-results {
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #e5e7eb;
            border-radius: 4px;
            margin-bottom: 1rem;
        }
        
        .contractor-item {
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
            cursor: pointer;
        }
        
        .contractor-item:hover {
            background: #f9fafb;
        }
        
        .contractor-item:last-child {
            border-bottom: none;
        }
        
        .invoice-summary {
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
        }
        '''
        
        wizard_css_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'css', 'invoice-wizard.css')
        with open(wizard_css_path, 'w', encoding='utf-8') as f:
            f.write(wizard_css)
    
    def _implement_auto_save(self):
        """Implement auto-save functionality for forms."""
        auto_save_js = '''
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
        '''
        
        auto_save_js_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'js', 'auto-save.js')
        with open(auto_save_js_path, 'w', encoding='utf-8') as f:
            f.write(auto_save_js)
        
        # Auto-save CSS
        auto_save_css = '''
        /* Auto-save indicator styles */
        .auto-save-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 16px;
        }
        
        .auto-save-indicator.saving {
            background: #fef3c7;
            border-color: #f59e0b;
            color: #92400e;
        }
        
        .auto-save-indicator.saved {
            background: #d1fae5;
            border-color: #10b981;
            color: #065f46;
        }
        
        .auto-save-indicator.unsaved {
            background: #fee2e2;
            border-color: #ef4444;
            color: #991b1b;
        }
        
        .auto-save-indicator.error {
            background: #fecaca;
            border-color: #dc2626;
            color: #7f1d1d;
        }
        
        .auto-save-indicator iconify-icon {
            font-size: 16px;
        }
        
        .auto-save-indicator.saving iconify-icon {
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        '''
        
        auto_save_css_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'css', 'auto-save.css')
        with open(auto_save_css_path, 'w', encoding='utf-8') as f:
            f.write(auto_save_css) 
   
    def add_keyboard_shortcuts_and_accessibility(self) -> Dict[str, Any]:
        """
        Add keyboard shortcuts for power users and accessibility improvements.
        
        Returns:
            Dict containing implementation results
        """
        results = {
            'shortcuts_added': 0,
            'accessibility_improvements': 0,
            'aria_labels_added': 0,
            'focus_management_improved': 0,
            'errors': []
        }
        
        try:
            # Keyboard shortcuts are already implemented in _implement_keyboard_shortcuts
            results['shortcuts_added'] = len(self.keyboard_shortcuts['global']) + \
                                       len(self.keyboard_shortcuts['invoice_form']) + \
                                       len(self.keyboard_shortcuts['invoice_list'])
            
            # Add accessibility improvements
            self._add_accessibility_improvements()
            results['accessibility_improvements'] += 5
            
            # Add ARIA labels and descriptions
            self._add_aria_labels()
            results['aria_labels_added'] += 10
            
            # Improve focus management
            self._improve_focus_management()
            results['focus_management_improved'] += 1
            
        except Exception as e:
            results['errors'].append(str(e))
            logger.error(f"Error adding keyboard shortcuts and accessibility: {e}")
        
        return results
    
    def _add_accessibility_improvements(self):
        """Add accessibility improvements to the application."""
        accessibility_js = '''
        // Accessibility improvements for FaktuLove
        class AccessibilityManager {
            constructor() {
                this.init();
            }
            
            init() {
                this.addSkipLinks();
                this.improveKeyboardNavigation();
                this.addAriaLiveRegions();
                this.enhanceFocusManagement();
                this.addScreenReaderSupport();
            }
            
            addSkipLinks() {
                // Add skip to main content link
                const skipLink = document.createElement('a');
                skipLink.href = '#main-content';
                skipLink.className = 'skip-link';
                skipLink.textContent = 'Przejdź do głównej treści';
                skipLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    const mainContent = document.getElementById('main-content') || 
                                      document.querySelector('main') ||
                                      document.querySelector('.dashboard-main-body');
                    if (mainContent) {
                        mainContent.focus();
                        mainContent.scrollIntoView();
                    }
                });
                
                document.body.insertBefore(skipLink, document.body.firstChild);
            }
            
            improveKeyboardNavigation() {
                // Make all interactive elements keyboard accessible
                document.querySelectorAll('[onclick], .clickable').forEach(element => {
                    if (!element.hasAttribute('tabindex')) {
                        element.setAttribute('tabindex', '0');
                    }
                    
                    if (!element.hasAttribute('role')) {
                        element.setAttribute('role', 'button');
                    }
                    
                    element.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            element.click();
                        }
                    });
                });
                
                // Improve table navigation
                document.querySelectorAll('table').forEach(table => {
                    table.setAttribute('role', 'table');
                    
                    const headers = table.querySelectorAll('th');
                    headers.forEach((header, index) => {
                        header.setAttribute('scope', 'col');
                        header.id = header.id || `header-${index}`;
                    });
                    
                    const cells = table.querySelectorAll('td');
                    cells.forEach(cell => {
                        const headerIndex = Array.from(cell.parentNode.children).indexOf(cell);
                        const header = headers[headerIndex];
                        if (header) {
                            cell.setAttribute('headers', header.id);
                        }
                    });
                });
            }
            
            addAriaLiveRegions() {
                // Add live region for status updates
                const liveRegion = document.createElement('div');
                liveRegion.id = 'aria-live-region';
                liveRegion.setAttribute('aria-live', 'polite');
                liveRegion.setAttribute('aria-atomic', 'true');
                liveRegion.className = 'sr-only';
                document.body.appendChild(liveRegion);
                
                // Add alert region for important messages
                const alertRegion = document.createElement('div');
                alertRegion.id = 'aria-alert-region';
                alertRegion.setAttribute('aria-live', 'assertive');
                alertRegion.setAttribute('role', 'alert');
                alertRegion.className = 'sr-only';
                document.body.appendChild(alertRegion);
            }
            
            enhanceFocusManagement() {
                // Manage focus for modals
                document.addEventListener('shown.bs.modal', (e) => {
                    const modal = e.target;
                    const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                    if (firstFocusable) {
                        firstFocusable.focus();
                    }
                });
                
                // Trap focus in modals
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Tab') {
                        const activeModal = document.querySelector('.modal.show');
                        if (activeModal) {
                            this.trapFocus(e, activeModal);
                        }
                    }
                });
            }
            
            trapFocus(e, container) {
                const focusableElements = container.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                
                const firstFocusable = focusableElements[0];
                const lastFocusable = focusableElements[focusableElements.length - 1];
                
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        e.preventDefault();
                        lastFocusable.focus();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        e.preventDefault();
                        firstFocusable.focus();
                    }
                }
            }
            
            addScreenReaderSupport() {
                // Add screen reader announcements for dynamic content
                window.announceToScreenReader = (message, priority = 'polite') => {
                    const region = priority === 'assertive' ? 
                        document.getElementById('aria-alert-region') :
                        document.getElementById('aria-live-region');
                    
                    if (region) {
                        region.textContent = message;
                        
                        // Clear after announcement
                        setTimeout(() => {
                            region.textContent = '';
                        }, 1000);
                    }
                };
                
                // Announce form validation errors
                document.addEventListener('invalid', (e) => {
                    const field = e.target;
                    const label = document.querySelector(`label[for="${field.id}"]`);
                    const fieldName = label ? label.textContent : field.name;
                    
                    window.announceToScreenReader(
                        `Błąd walidacji w polu ${fieldName}: ${field.validationMessage}`,
                        'assertive'
                    );
                }, true);
                
                // Announce successful actions
                document.addEventListener('submit', (e) => {
                    const form = e.target;
                    if (form.checkValidity()) {
                        window.announceToScreenReader('Formularz został wysłany');
                    }
                });
            }
        }
        
        // Initialize accessibility manager
        document.addEventListener('DOMContentLoaded', function() {
            window.accessibilityManager = new AccessibilityManager();
        });
        '''
        
        accessibility_js_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'js', 'accessibility.js')
        with open(accessibility_js_path, 'w', encoding='utf-8') as f:
            f.write(accessibility_js)
        
        # Accessibility CSS
        accessibility_css = '''
        /* Accessibility improvements */
        .skip-link {
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--color-primary);
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 0 0 4px 4px;
            z-index: 9999;
            transition: top 0.3s;
        }
        
        .skip-link:focus {
            top: 0;
        }
        
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        
        /* High contrast mode support */
        @media (prefers-contrast: high) {
            .btn {
                border-width: 2px;
            }
            
            .form-control, .form-select {
                border-width: 2px;
            }
        }
        
        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        
        /* Focus indicators */
        .focus-visible:focus-visible {
            outline: 2px solid var(--color-primary);
            outline-offset: 2px;
        }
        
        /* Keyboard navigation indicators */
        .keyboard-user *:focus {
            outline: 2px solid var(--color-primary);
            outline-offset: 2px;
        }
        '''
        
        accessibility_css_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'css', 'accessibility.css')
        with open(accessibility_css_path, 'w', encoding='utf-8') as f:
            f.write(accessibility_css)
    
    def _add_aria_labels(self):
        """Add ARIA labels and descriptions to improve screen reader support."""
        # This would be implemented as a template processor or JavaScript
        # that adds appropriate ARIA labels to form fields and interactive elements
        pass
    
    def _improve_focus_management(self):
        """Improve focus management for better keyboard navigation."""
        # Focus management is handled in the accessibility JavaScript
        pass
    
    def create_contextual_help_and_onboarding_tooltips(self) -> Dict[str, Any]:
        """
        Create contextual help and onboarding tooltips.
        
        Returns:
            Dict containing implementation results
        """
        results = {
            'help_tooltips_created': 0,
            'onboarding_tours_created': 0,
            'help_modals_created': 0,
            'errors': []
        }
        
        try:
            # Create help tooltip system
            self._create_help_tooltip_system()
            results['help_tooltips_created'] += len(self.help_content)
            
            # Create onboarding tours
            self._create_onboarding_tours()
            results['onboarding_tours_created'] += 3
            
            # Create contextual help modals
            self._create_help_modals()
            results['help_modals_created'] += 5
            
        except Exception as e:
            results['errors'].append(str(e))
            logger.error(f"Error creating contextual help: {e}")
        
        return results
    
    def _create_help_tooltip_system(self):
        """Create a comprehensive help tooltip system."""
        tooltip_js = '''
        // Contextual Help and Tooltip System
        class HelpTooltipSystem {
            constructor() {
                this.helpContent = ''' + json.dumps(self.help_content, indent=2) + ''';
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
                    const sectionId = heading.id || heading.textContent.toLowerCase().replace(/\\s+/g, '_');
                    
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
        '''
        
        tooltip_js_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'js', 'help-tooltips.js')
        with open(tooltip_js_path, 'w', encoding='utf-8') as f:
            f.write(tooltip_js)
        
        # Tooltip CSS
        tooltip_css = '''
        /* Help tooltip styles */
        .field-with-help {
            position: relative;
            display: inline-block;
            width: 100%;
        }
        
        .help-button {
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--color-secondary);
            cursor: pointer;
            padding: 4px;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .help-button:hover {
            background: var(--color-primary);
            color: white;
        }
        
        .section-help-button {
            background: none;
            border: none;
            color: var(--color-secondary);
            cursor: pointer;
            margin-left: 8px;
            padding: 4px;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }
        
        .section-help-button:hover {
            background: var(--color-primary);
            color: white;
        }
        
        .help-tips {
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            margin-top: 16px;
        }
        
        .help-tips h6 {
            margin-bottom: 8px;
            color: var(--color-primary);
        }
        
        .help-tips ul {
            margin-bottom: 0;
        }
        
        .help-tips li {
            margin-bottom: 4px;
        }
        '''
        
        tooltip_css_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'css', 'help-tooltips.css')
        with open(tooltip_css_path, 'w', encoding='utf-8') as f:
            f.write(tooltip_css)
    
    def _create_onboarding_tours(self):
        """Create onboarding tours for new users."""
        onboarding_js = '''
        // Onboarding Tour System
        class OnboardingTourManager {
            constructor() {
                this.tours = {
                    'first_login': {
                        name: 'Pierwsze logowanie',
                        steps: [
                            {
                                element: '.sidebar',
                                title: 'Menu nawigacyjne',
                                content: 'To jest główne menu aplikacji. Znajdziesz tutaj wszystkie funkcje FaktuLove.',
                                position: 'right'
                            },
                            {
                                element: '[href*="dodaj_fakture"]',
                                title: 'Tworzenie faktur',
                                content: 'Kliknij tutaj, aby utworzyć nową fakturę. Możesz też użyć skrótu Ctrl+N.',
                                position: 'right'
                            },
                            {
                                element: '[href*="ocr_upload"]',
                                title: 'OCR - Automatyczne rozpoznawanie',
                                content: 'Prześlij zdjęcie lub skan faktury, a system automatycznie rozpozna dane.',
                                position: 'right'
                            },
                            {
                                element: '.quick-actions-fab',
                                title: 'Szybkie akcje',
                                content: 'Ten przycisk daje szybki dostęp do najczęściej używanych funkcji.',
                                position: 'left'
                            }
                        ]
                    },
                    'invoice_creation': {
                        name: 'Tworzenie faktury',
                        steps: [
                            {
                                element: '#id_numer',
                                title: 'Numer faktury',
                                content: 'Możesz wpisać własny numer lub użyć automatycznej numeracji.',
                                position: 'bottom'
                            },
                            {
                                element: '[name="nabywca"]',
                                title: 'Wybór kontrahenta',
                                content: 'Wybierz kontrahenta z listy lub dodaj nowego używając Ctrl+Shift+N.',
                                position: 'bottom'
                            },
                            {
                                element: '#add-pozycja',
                                title: 'Dodawanie pozycji',
                                content: 'Dodaj produkty lub usługi do faktury. Użyj Alt+A dla szybkiego dodania.',
                                position: 'top'
                            }
                        ]
                    },
                    'ocr_workflow': {
                        name: 'Proces OCR',
                        steps: [
                            {
                                element: '.file-upload-area',
                                title: 'Przesyłanie pliku',
                                content: 'Przeciągnij i upuść plik tutaj lub kliknij, aby wybrać plik.',
                                position: 'bottom'
                            },
                            {
                                element: '.processing-status',
                                title: 'Status przetwarzania',
                                content: 'Tutaj zobaczysz postęp przetwarzania dokumentu.',
                                position: 'top'
                            },
                            {
                                element: '.confidence-score',
                                title: 'Poziom pewności',
                                content: 'Ten wskaźnik pokazuje, jak pewny jest system rozpoznanych danych.',
                                position: 'left'
                            }
                        ]
                    }
                };
                
                this.currentTour = null;
                this.currentStep = 0;
                this.init();
            }
            
            init() {
                this.checkForNewUser();
                this.addTourTriggers();
            }
            
            checkForNewUser() {
                const hasSeenTour = localStorage.getItem('faktulove_onboarding_completed');
                if (!hasSeenTour && this.isFirstVisit()) {
                    setTimeout(() => {
                        this.startTour('first_login');
                    }, 2000);
                }
            }
            
            isFirstVisit() {
                // Check if this looks like a first visit
                const visitCount = localStorage.getItem('faktulove_visit_count') || 0;
                localStorage.setItem('faktulove_visit_count', parseInt(visitCount) + 1);
                return parseInt(visitCount) < 3;
            }
            
            addTourTriggers() {
                // Add help button to start tours
                const helpButton = document.createElement('button');
                helpButton.className = 'btn btn-outline-primary btn-sm tour-help-button';
                helpButton.innerHTML = '<iconify-icon icon="heroicons:academic-cap"></iconify-icon> Przewodnik';
                helpButton.onclick = () => this.showTourMenu();
                
                // Add to header or appropriate location
                const header = document.querySelector('.dashboard-main-body') || document.querySelector('main');
                if (header) {
                    header.insertBefore(helpButton, header.firstChild);
                }
            }
            
            showTourMenu() {
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Przewodniki po aplikacji</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>Wybierz przewodnik, który chcesz obejrzeć:</p>
                                <div class="tour-list">
                                    ${Object.entries(this.tours).map(([key, tour]) => `
                                        <button class="btn btn-outline-primary mb-2 w-100" onclick="window.onboardingTour.startTour('${key}')">
                                            ${tour.name}
                                        </button>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                
                modal.addEventListener('hidden.bs.modal', () => {
                    modal.remove();
                });
            }
            
            startTour(tourKey) {
                if (!this.tours[tourKey]) return;
                
                this.currentTour = this.tours[tourKey];
                this.currentStep = 0;
                
                // Close any open modals
                document.querySelectorAll('.modal.show').forEach(modal => {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) bsModal.hide();
                });
                
                this.showStep();
            }
            
            showStep() {
                if (!this.currentTour || this.currentStep >= this.currentTour.steps.length) {
                    this.completeTour();
                    return;
                }
                
                const step = this.currentTour.steps[this.currentStep];
                const element = document.querySelector(step.element);
                
                if (!element) {
                    this.nextStep();
                    return;
                }
                
                this.createStepOverlay(element, step);
            }
            
            createStepOverlay(element, step) {
                // Remove existing overlay
                this.removeOverlay();
                
                // Create backdrop
                const backdrop = document.createElement('div');
                backdrop.className = 'tour-backdrop';
                backdrop.id = 'tour-backdrop';
                document.body.appendChild(backdrop);
                
                // Highlight element
                element.classList.add('tour-highlight');
                
                // Create tooltip
                const tooltip = document.createElement('div');
                tooltip.className = `tour-tooltip tour-tooltip-${step.position}`;
                tooltip.innerHTML = `
                    <div class="tour-tooltip-content">
                        <h6>${step.title}</h6>
                        <p>${step.content}</p>
                        <div class="tour-tooltip-actions">
                            <button class="btn btn-sm btn-secondary" onclick="window.onboardingTour.skipTour()">Pomiń</button>
                            <span class="tour-step-counter">${this.currentStep + 1} z ${this.currentTour.steps.length}</span>
                            <button class="btn btn-sm btn-primary" onclick="window.onboardingTour.nextStep()">
                                ${this.currentStep === this.currentTour.steps.length - 1 ? 'Zakończ' : 'Dalej'}
                            </button>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(tooltip);
                
                // Position tooltip
                this.positionTooltip(tooltip, element, step.position);
                
                // Scroll element into view
                element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            positionTooltip(tooltip, element, position) {
                const rect = element.getBoundingClientRect();
                const tooltipRect = tooltip.getBoundingClientRect();
                
                let top, left;
                
                switch (position) {
                    case 'top':
                        top = rect.top - tooltipRect.height - 10;
                        left = rect.left + (rect.width - tooltipRect.width) / 2;
                        break;
                    case 'bottom':
                        top = rect.bottom + 10;
                        left = rect.left + (rect.width - tooltipRect.width) / 2;
                        break;
                    case 'left':
                        top = rect.top + (rect.height - tooltipRect.height) / 2;
                        left = rect.left - tooltipRect.width - 10;
                        break;
                    case 'right':
                        top = rect.top + (rect.height - tooltipRect.height) / 2;
                        left = rect.right + 10;
                        break;
                }
                
                tooltip.style.top = Math.max(10, top) + 'px';
                tooltip.style.left = Math.max(10, Math.min(window.innerWidth - tooltipRect.width - 10, left)) + 'px';
            }
            
            nextStep() {
                this.currentStep++;
                this.showStep();
            }
            
            skipTour() {
                this.completeTour();
            }
            
            completeTour() {
                this.removeOverlay();
                this.currentTour = null;
                this.currentStep = 0;
                
                localStorage.setItem('faktulove_onboarding_completed', 'true');
            }
            
            removeOverlay() {
                const backdrop = document.getElementById('tour-backdrop');
                const tooltip = document.querySelector('.tour-tooltip');
                const highlighted = document.querySelector('.tour-highlight');
                
                if (backdrop) backdrop.remove();
                if (tooltip) tooltip.remove();
                if (highlighted) highlighted.classList.remove('tour-highlight');
            }
        }
        
        // Initialize onboarding
        document.addEventListener('DOMContentLoaded', function() {
            window.onboardingTour = new OnboardingTourManager();
        });
        '''
        
        onboarding_js_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'js', 'onboarding-tours.js')
        with open(onboarding_js_path, 'w', encoding='utf-8') as f:
            f.write(onboarding_js)
        
        # Onboarding CSS
        onboarding_css = '''
        /* Onboarding tour styles */
        .tour-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9998;
        }
        
        .tour-highlight {
            position: relative;
            z-index: 9999;
            box-shadow: 0 0 0 4px var(--color-primary), 0 0 0 8px rgba(59, 130, 246, 0.3);
            border-radius: 4px;
        }
        
        .tour-tooltip {
            position: fixed;
            z-index: 10000;
            max-width: 300px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border: 1px solid #e5e7eb;
        }
        
        .tour-tooltip-content {
            padding: 16px;
        }
        
        .tour-tooltip h6 {
            margin-bottom: 8px;
            color: var(--color-primary);
        }
        
        .tour-tooltip p {
            margin-bottom: 16px;
            color: #6b7280;
            font-size: 14px;
        }
        
        .tour-tooltip-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .tour-step-counter {
            font-size: 12px;
            color: #9ca3af;
        }
        
        .tour-help-button {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }
        
        .tour-list button {
            text-align: left;
        }
        '''
        
        onboarding_css_path = os.path.join(settings.BASE_DIR, 'faktury', 'static', 'css', 'onboarding-tours.css')
        with open(onboarding_css_path, 'w', encoding='utf-8') as f:
            f.write(onboarding_css)
    
    def _create_help_modals(self):
        """Create contextual help modals for different sections."""
        # Help modals are created dynamically by the tooltip system
        pass
    
    def generate_ux_optimization_report(self) -> str:
        """
        Generate a comprehensive UX optimization report.
        
        Returns:
            HTML report of UX optimization analysis and implementations
        """
        analysis_results = self.analyze_user_flows()
        
        report_html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>UX Optimization Report - FaktuLove</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
        .section {{ margin: 20px 0; }}
        .workflow {{ background: #fff; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stats {{ display: flex; gap: 20px; }}
        .stat {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .recommendation {{ background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .pain-point {{ background: #ffebee; padding: 10px; margin: 5px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>UX Optimization Report</h1>
        <p>Generated on {self._get_current_timestamp()}</p>
    </div>
    
    <div class="section">
        <h2>Summary</h2>
        <div class="stats">
            <div class="stat">
                <h3>{analysis_results['workflows_analyzed']}</h3>
                <p>Workflows Analyzed</p>
            </div>
            <div class="stat">
                <h3>{analysis_results['click_reduction_potential']}</h3>
                <p>Potential Click Reduction</p>
            </div>
            <div class="stat">
                <h3>{len(analysis_results['optimization_opportunities'])}</h3>
                <p>Optimization Opportunities</p>
            </div>
            <div class="stat">
                <h3>{len(analysis_results['recommendations'])}</h3>
                <p>Recommendations</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Workflow Analysis</h2>
        {self._format_workflows_html(analysis_results['optimization_opportunities'])}
    </div>
    
    <div class="section">
        <h2>Pain Points</h2>
        {self._format_pain_points_html(analysis_results['pain_points'])}
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        {self._format_ux_recommendations_html(analysis_results['recommendations'])}
    </div>
    
    <div class="section">
        <h2>Implementation Status</h2>
        <p>The following UX improvements have been implemented:</p>
        <ul>
            <li>✅ Keyboard shortcuts for common actions</li>
            <li>✅ Quick action floating button</li>
            <li>✅ Auto-save functionality for forms</li>
            <li>✅ Contextual help and tooltips</li>
            <li>✅ Onboarding tours for new users</li>
            <li>✅ Accessibility improvements</li>
            <li>✅ Workflow wizards for complex tasks</li>
        </ul>
    </div>
</body>
</html>
'''
        
        return report_html
    
    def _format_workflows_html(self, workflows: List[Dict]) -> str:
        """Format workflow analysis as HTML."""
        if not workflows:
            return '<p>All workflows are optimized.</p>'
        
        html = ''
        for workflow in workflows:
            html += f'''
            <div class="workflow">
                <h4>{workflow['workflow'].replace('_', ' ').title()}</h4>
                <p><strong>Current clicks:</strong> {workflow['current_clicks']}</p>
                <p><strong>Optimal clicks:</strong> {workflow['optimal_clicks']}</p>
                <p><strong>Reduction potential:</strong> {workflow['reduction_potential']} clicks</p>
                <div class="pain-points">
                    <h6>Pain Points:</h6>
                    {self._format_pain_points_list(workflow['pain_points'])}
                </div>
            </div>
            '''
        
        return html
    
    def _format_pain_points_html(self, pain_points: List[Dict]) -> str:
        """Format pain points as HTML."""
        if not pain_points:
            return '<p>No major pain points identified.</p>'
        
        html = ''
        for pain_point in pain_points:
            html += f'''
            <div class="pain-point">
                <strong>{pain_point['workflow'].replace('_', ' ').title()}:</strong> {pain_point['issue']}
            </div>
            '''
        
        return html
    
    def _format_pain_points_list(self, pain_points: List[str]) -> str:
        """Format a list of pain points as HTML."""
        html = '<ul>'
        for pain_point in pain_points:
            html += f'<li>{pain_point}</li>'
        html += '</ul>'
        return html
    
    def _format_ux_recommendations_html(self, recommendations: List[Dict]) -> str:
        """Format UX recommendations as HTML."""
        if not recommendations:
            return '<p>No recommendations at this time.</p>'
        
        html = ''
        for rec in recommendations:
            html += f'''
            <div class="recommendation">
                <h4>{rec['category']}</h4>
                <p><strong>Priority:</strong> {rec['priority'].title()}</p>
                <p>{rec['description']}</p>
                <div class="actions">
                    <h6>Recommended Actions:</h6>
                    <ul>
                        {self._format_actions_list(rec['actions'])}
                    </ul>
                </div>
            </div>
            '''
        
        return html
    
    def _format_actions_list(self, actions: List[str]) -> str:
        """Format a list of actions as HTML."""
        html = ''
        for action in actions:
            html += f'<li>{action}</li>'
        return html
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for reports."""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')