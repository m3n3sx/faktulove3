
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
        