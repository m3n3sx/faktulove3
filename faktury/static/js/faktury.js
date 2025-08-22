// FIXED VERSION - Live calculations for invoice forms
document.addEventListener('DOMContentLoaded', function() {

    // -------------------------------------------------
    // Pobierz referencje do elementów DOM - RAZ, na początku
    // -------------------------------------------------

    // Kontrahent
    const nipInput = document.querySelector('#id_nabywca_nip');
    const pobierzDaneGUSButton = document.querySelector('#pobierz-dane-gus');
    const kontrahentSelect = document.querySelector('#id_nabywca');
    const firmaRadio = document.querySelector('#firma');
    const osobaPrywatnaRadio = document.querySelector('#osoba_prywatna');
    const saveButton = document.querySelector('#zapisz-kontrahenta');
    const nazwaInput = document.querySelector('#id_nabywca_nazwa');
    const ulicaInput = document.querySelector('#id_nabywca_ulica');
    const numerDomuInput = document.querySelector('#id_nabywca_numer_domu');
    const numerMieszkaniaInput = document.querySelector('#id_nabywca_numer_mieszkania');
    const kodPocztowyInput = document.querySelector('#id_nabywca_kod_pocztowy');
    const miejscowoscInput = document.querySelector('#id_nabywca_miejscowosc');
    const krajInput = document.querySelector('#id_nabywca_kraj');
    
    // FIXED: Pozycje Faktury - use correct container ID
    const ukryjRabatButton = document.querySelector('#ukryj-rabat');
    const addButton = document.querySelector("#add-pozycja");
    const totalForms = document.querySelector("#id_pozycje-TOTAL_FORMS");
    const container = document.querySelector("#faktura-pozycje"); // FIXED: Use correct ID
    
    // Użyj querySelectorAll *raz*, na początku
    let pozycjaForm = document.querySelectorAll(".pozycja-form");
    let formNum = pozycjaForm.length - 1;

    // Funkcja pomocnicza do obsługi odpowiedzi fetch i błędów.
    function handleFetchResponse(response) {
        if (!response.ok) {
            throw new Error(`Błąd HTTP: ${response.status}`);
        }
        return response.json();
    }

    function displayErrorMessage(message) {
        console.error(message);
        alert(message);
    }

    // -------------------------------------------------------------
    // 1. Obsługa pobierania danych kontrahenta z GUS
    // -------------------------------------------------------------

    if (pobierzDaneGUSButton && nipInput) {
        pobierzDaneGUSButton.addEventListener("click", function() {
            let nip = nipInput.value;
    
            if (!nip) {
                displayErrorMessage('Wprowadź NIP');
                return;
            }

            fetch(`/pobierz_dane_z_gus/?nip=${nip}`)
                .then(response => response.json())
                .then(data => {
                    if (!data.error) {
                        if (nazwaInput) nazwaInput.value = data.data.Nazwa || '';
                        if (ulicaInput) ulicaInput.value = data.data.Ulica || '';
                        if (kodPocztowyInput) kodPocztowyInput.value = data.data.KodPocztowy || '';
                        if (miejscowoscInput) miejscowoscInput.value = data.data.Miejscowosc || '';
                    } else {
                        displayErrorMessage(data.error);
                    }
                })
                .catch(error => {
                    console.error("Błąd:", error);
                    displayErrorMessage("Wystąpił błąd podczas pobierania danych z GUS");
                });
        });
    }

    // -------------------------------------------------------------
    // 2. Obsługa wybierania kontrahenta z listy (dropdown)
    // -------------------------------------------------------------
    if (kontrahentSelect) {
        kontrahentSelect.addEventListener('change', function() {
            const selectedKontrahentId = this.value;
            if (selectedKontrahentId) {
                fetch(`/pobierz_dane_kontrahenta/?id=${selectedKontrahentId}`)
                .then(handleFetchResponse)
                .then(data => {
                    if (nazwaInput) nazwaInput.value = data.nazwa || '';
                    if (ulicaInput) ulicaInput.value = data.ulica || '';
                    if (numerDomuInput) numerDomuInput.value = data.numer_domu || '';
                    if (numerMieszkaniaInput) numerMieszkaniaInput.value = data.numer_mieszkania || '';
                    if (kodPocztowyInput) kodPocztowyInput.value = data.kod_pocztowy || '';
                    if (miejscowoscInput) miejscowoscInput.value = data.miejscowosc || '';
                    if (nipInput) nipInput.value = data.nip || '';
                    if (krajInput) krajInput.value = data.kraj || '';

                    if (data.czy_firma) {
                        if (firmaRadio) firmaRadio.checked = true;
                    } else {
                        if (osobaPrywatnaRadio) osobaPrywatnaRadio.checked = true;
                    }
                    toggleNipField();
                })
                .catch(error => {
                    console.error("Błąd pobierania danych kontrahenta:", error);
                    displayErrorMessage("Wystąpił błąd podczas pobierania danych kontrahenta.");
                });
            }
        });
    }

    // FIXED: Helper function to create a new row with proper structure
    function createRow() {
        const totalFormsElement = document.getElementById('id_pozycje-TOTAL_FORMS');
        if (!totalFormsElement) {
            console.error('TOTAL_FORMS element not found');
            return null;
        }
        
        const newIndex = parseInt(totalFormsElement.value);
        const emptyFormElement = document.getElementById('empty-form');
        
        if (!emptyFormElement) {
            console.error('Empty form template not found');
            return null;
        }
        
        // Clone the empty form element
        const emptyForm = emptyFormElement.cloneNode(true);
        emptyForm.id = ''; // Remove the ID to avoid duplicates
        emptyForm.style.display = ''; // Make sure it's visible
        
        // Update all the form field names and IDs
        const inputs = emptyForm.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.name) {
                input.name = input.name.replace('__prefix__', newIndex);
            }
            if (input.id) {
                input.id = input.id.replace('__prefix__', newIndex);
            }
        });
        
        // Update labels
        const labels = emptyForm.querySelectorAll('label');
        labels.forEach(label => {
            if (label.htmlFor) {
                label.htmlFor = label.htmlFor.replace('__prefix__', newIndex);
            }
        });
        
        // Initialize event listeners for the new row
        addFormListeners(emptyForm);
        addProduktSelectionListener(emptyForm);
        
        // Add delete button functionality
        const deleteBtn = emptyForm.querySelector('.usun-pozycje');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                const deleteCheckbox = emptyForm.querySelector('input[name$="-DELETE"]');
                if (deleteCheckbox) {
                    deleteCheckbox.checked = true;
                    emptyForm.style.display = 'none';
                    updateTotals();
                }
            });
        }
      
        totalFormsElement.value = newIndex + 1;
        return emptyForm;
    }

    // -------------------------------------------------------------
    // 3. Obsługa dodawania pozycji faktury (i obliczeń)
    // -------------------------------------------------------------

    if (addButton && container) {
        addButton.addEventListener('click', addPozycjaForm);

        // Delegacja zdarzeń dla przycisków usuwania (istniejące wiersze)
        container.addEventListener('click', function(event) {
            if (event.target.classList.contains('usun-pozycje')) {
                const row = event.target.closest('.pozycja-form');
                const deleteInput = row.querySelector('input[type="checkbox"][name$="DELETE"]');
                if (deleteInput) {
                    deleteInput.checked = true;
                }
                row.style.display = 'none';
                updateTotals();
            }
        });
    }

    function addPozycjaForm() {
        try {
            if (!container) {
                displayErrorMessage("Kontener dla pozycji faktury nie został znaleziony");
                return;
            }
            
            let newForm = createRow();
            if (!newForm) {
                displayErrorMessage("Nie można utworzyć nowego wiersza");
                return;
            }
            
            container.appendChild(newForm);
            
            // Wyczyść wartości wejściowe w nowym formularzu
            let inputs = newForm.querySelectorAll('input:not([type="checkbox"]):not([type="hidden"])');
            inputs.forEach(input => {
                input.value = '';
            });

            let selects = newForm.querySelectorAll('select');
            selects.forEach(select => {
                select.selectedIndex = 0;
            });

            // Reset calculated values
            const nettoCol = newForm.querySelector('.wartosc-netto-col');
            const bruttoCol = newForm.querySelector('.wartosc-brutto-col');
            if (nettoCol) nettoCol.textContent = '0.00';
            if (bruttoCol) bruttoCol.textContent = '0.00';

            updateTotals();
            console.log('New position added successfully');

        } catch (error) {
            console.error("Error adding position form:", error);
            displayErrorMessage("Wystąpił błąd podczas dodawania pozycji faktury: " + error.message);
        }
    }

    // FIXED: Dodaje listenery do *pojedynczego* wiersza formularza z prawidłowymi selektorami
    function addFormListeners(form) {
        const fields = [
            'input[name$="ilosc"]',
            'input[name$="cena_netto"]',
            'select[name$="vat"]',  // FIXED: VAT is select field
            'input[name$="rabat"]',
            'select[name$="rabat_typ"]',
        ];

        fields.forEach(selector => {
            const elements = form.querySelectorAll(selector);
            elements.forEach(element => {
                // Remove existing listeners to prevent duplicates
                element.removeEventListener('change', handleFieldChange);
                element.removeEventListener('keyup', handleFieldChange);
                element.removeEventListener('input', handleFieldChange);
                
                // Add new listeners
                element.addEventListener('change', handleFieldChange);
                element.addEventListener('keyup', handleFieldChange);
                element.addEventListener('input', handleFieldChange);  // For real-time input
            });
        });
    }

    // FIXED: Dedicated event handler function
    function handleFieldChange(event) {
        const form = event.target.closest('.pozycja-form');
        if (form) {
            updateRowValues(event, form);
        }
    }

    // FIXED: Dodaje listener zmiany wyboru produktu do *pojedynczego* wiersza formularza
    function addProduktSelectionListener(form) {
        const produktSelect = form.querySelector('.produkt-select');
        if (!produktSelect) return;
        
        const nazwaInput = form.querySelector('input[name$="nazwa"]');
        const cenaNettoInput = form.querySelector('input[name$="cena_netto"]');
        const vatSelect = form.querySelector('select[name$="vat"]');
        const jednostkaField = form.querySelector('[name$="jednostka"]'); // FIXED: Can be input or select
    
        // Remove existing listener to prevent duplicates
        produktSelect.removeEventListener('change', produktSelect._changeHandler);
        
        // Create and store the change handler
        produktSelect._changeHandler = function() {
            const selectedProduktId = this.value;
            if (!selectedProduktId) {
                // Reset fields when no product selected
                if (nazwaInput) nazwaInput.value = '';
                if (cenaNettoInput) cenaNettoInput.value = '';
                if (vatSelect) vatSelect.value = '';
                if (jednostkaField) jednostkaField.value = '';
                updateRowValues(null, form);
                return;
            }
    
            // Send API request
            fetch(`/pobierz_dane_produktu/?id=${selectedProduktId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Błąd HTTP: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        displayErrorMessage(data.error);
                        return;
                    }
    
                    // Update form fields
                    if (nazwaInput) nazwaInput.value = data.nazwa || '';
                    if (cenaNettoInput) cenaNettoInput.value = data.cena_netto || '';
                    if (vatSelect) vatSelect.value = data.vat || '';
                    if (jednostkaField) jednostkaField.value = data.jednostka || '';
                    
                    // Trigger calculation after setting values
                    updateRowValues(null, form);
                })
                .catch(error => {
                    console.error('Błąd:', error);
                    displayErrorMessage(`Wystąpił błąd podczas pobierania danych produktu: ${error.message}`);
                });
        };
        
        produktSelect.addEventListener('change', produktSelect._changeHandler);
    }

    // FIXED: Improved updateRowValues function with better error handling
    function updateRowValues(event, form) {
        try {
            // Handle case where event is null (when called from product selection)
            const row = event ? event.target.closest('.pozycja-form') : form.closest('.pozycja-form') || form;
            if (!row) return;
            
            // Skip deleted rows
            const deleteInput = row.querySelector('input[type="checkbox"][name$="DELETE"]');
            if (deleteInput && deleteInput.checked) {
                return;
            }
        
            // Get field values with fallbacks
            const iloscInput = row.querySelector('input[name$="ilosc"]');
            const cenaNettoInput = row.querySelector('input[name$="cena_netto"]');
            const vatSelect = row.querySelector('select[name$="vat"]');
            const rabatInput = row.querySelector('input[name$="rabat"]');
            const rabatTypSelect = row.querySelector('select[name$="rabat_typ"]');
            
            const ilosc = parseFloat(iloscInput?.value) || 0;
            const cena_netto = parseFloat(cenaNettoInput?.value) || 0;
            const vat = vatSelect?.value === 'zw' ? 0 : parseFloat(vatSelect?.value) || 0;
            const rabat = parseFloat(rabatInput?.value) || 0;
            const rabat_typ = rabatTypSelect?.value || 'procent';
        
            let wartosc_netto = ilosc * cena_netto;
            
            // Apply discount
            if (rabat_typ === 'procent' && rabat > 0) {
                wartosc_netto = wartosc_netto * (1 - rabat / 100);
            } else if (rabat_typ === 'kwota' && rabat > 0) {
                wartosc_netto = wartosc_netto - rabat;
            }
        
            wartosc_netto = Math.max(0, parseFloat(wartosc_netto.toFixed(2)));
            const wartosc_vat = wartosc_netto * (vat / 100);
            const wartosc_brutto = wartosc_netto + wartosc_vat;
        
            // Update display columns
            const nettoCol = row.querySelector('.wartosc-netto-col');
            const bruttoCol = row.querySelector('.wartosc-brutto-col');
            
            if (nettoCol) nettoCol.textContent = wartosc_netto.toFixed(2);
            if (bruttoCol) bruttoCol.textContent = wartosc_brutto.toFixed(2);
        
            updateTotals();
            
        } catch (error) {
            console.error('Error in updateRowValues:', error);
        }
    }

    // FIXED: Improved updateTotals function with better error handling
    function updateTotals() {
        try {
            let sumaNettoPrzedRabatem = 0;
            let sumaRabatow = 0;
            let sumaNettoPoRabacie = 0;
            let sumaVat = 0;
            let sumaBrutto = 0;

            document.querySelectorAll('.pozycja-form').forEach(row => {
                // Skip deleted rows and hidden rows
                const deleteInput = row.querySelector('input[type="checkbox"][name$="DELETE"]');
                if ((deleteInput && deleteInput.checked) || row.style.display === 'none') {
                    return;
                }

                const iloscInput = row.querySelector('input[name$="ilosc"]');
                const cenaNettoInput = row.querySelector('input[name$="cena_netto"]');
                const rabatInput = row.querySelector('input[name$="rabat"]');
                const rabatTypSelect = row.querySelector('select[name$="rabat_typ"]');
                const vatSelect = row.querySelector('select[name$="vat"]');

                const ilosc = parseFloat(iloscInput?.value) || 0;
                const cena_netto = parseFloat(cenaNettoInput?.value) || 0;
                const rabat = parseFloat(rabatInput?.value) || 0;
                const rabat_typ = rabatTypSelect?.value || 'procent';
                const vat = vatSelect?.value === 'zw' ? 0 : parseFloat(vatSelect?.value) || 0;

                sumaNettoPrzedRabatem += ilosc * cena_netto;

                let wartosc_netto = ilosc * cena_netto;
                let rabat_wartosc = 0;

                if (rabat_typ === 'procent' && rabat > 0) {
                    rabat_wartosc = wartosc_netto * (rabat / 100);
                    wartosc_netto = wartosc_netto * (1 - rabat / 100);
                } else if (rabat_typ === 'kwota' && rabat > 0) {
                    rabat_wartosc = rabat;
                    wartosc_netto = wartosc_netto - rabat;
                }
                
                sumaRabatow += rabat_wartosc;
                wartosc_netto = Math.max(0, parseFloat(wartosc_netto.toFixed(2)));
                sumaNettoPoRabacie += wartosc_netto;
                
                let wartosc_vat = wartosc_netto * (vat / 100);
                sumaVat += wartosc_vat;
                sumaBrutto += wartosc_netto + wartosc_vat;
            });

            // Update total displays with error checking
            const elements = {
                '.suma-netto-przed-rabatem': sumaNettoPrzedRabatem.toFixed(2),
                '.suma-rabatu': sumaRabatow.toFixed(2),
                '.suma-netto-po-rabacie': sumaNettoPoRabacie.toFixed(2),
                '.suma-vat': sumaVat.toFixed(2),
                '.suma-brutto': sumaBrutto.toFixed(2)
            };

            Object.entries(elements).forEach(([selector, value]) => {
                const element = document.querySelector(selector);
                if (element) {
                    element.textContent = value;
                }
            });
            
        } catch (error) {
            console.error("Błąd podczas aktualizacji sum:", error);
        }
    }

    // --- Inicjalizacja (po załadowaniu DOM) ---
    // Dodaj listenery do *istniejących* formularzy
    if (pozycjaForm.length > 0) {
        pozycjaForm.forEach(form => {
            // Skip the empty form template
            if (form.id !== 'empty-form') {
                addFormListeners(form);
                addProduktSelectionListener(form);
            }
        });
        updateTotals();
    }

    // -------------------------------------------------------------
    // 4. Obsługa radio buttonów Firma/Osoba prywatna
    // -------------------------------------------------------------

    function toggleNipField() {
        if (osobaPrywatnaRadio && osobaPrywatnaRadio.checked) {
            if (nipInput) {
                nipInput.value = '';
                nipInput.disabled = true;
                nipInput.style.display = 'none';
            }
            if (pobierzDaneGUSButton) {
                pobierzDaneGUSButton.disabled = true;
                pobierzDaneGUSButton.style.display = 'none';
            }
        } else {
            if (nipInput) {
                nipInput.disabled = false;
                nipInput.style.display = 'block';
            }
            if (pobierzDaneGUSButton) {
                pobierzDaneGUSButton.disabled = false;
                pobierzDaneGUSButton.style.display = 'block';
            }
        }
    }

    if (firmaRadio && osobaPrywatnaRadio) {
        firmaRadio.addEventListener('change', toggleNipField);
        osobaPrywatnaRadio.addEventListener('change', toggleNipField);
        toggleNipField();
    }

    // -------------------------------------------------------------
    // 5. Obsługa zapisu kontrahenta
    // -------------------------------------------------------------

    if (saveButton) {
        saveButton.addEventListener('click', function() {
            const nip = nipInput?.value || '';
            const nazwa = nazwaInput?.value || '';
            const ulica = ulicaInput?.value || '';
            const numer_domu = numerDomuInput?.value || '';
            const numer_mieszkania = numerMieszkaniaInput?.value || '';
            const kod_pocztowy = kodPocztowyInput?.value || '';
            const miejscowosc = miejscowoscInput?.value || '';
            const kraj = krajInput?.value || '';
            const czy_firma = firmaRadio?.checked || false;

            if (!nazwa || (czy_firma && !nip) || !ulica || !numer_domu || !kod_pocztowy || !miejscowosc) {
                displayErrorMessage('Wypełnij wszystkie wymagane pola (dla firmy: Nazwa, NIP, Ulica, Numer domu, Kod pocztowy, Miejscowość; dla osoby prywatnej: Nazwa, Ulica, Numer domu, Kod pocztowy, Miejscowość).');
                return;
            }

            const params = new URLSearchParams({
                nip, nazwa, ulica, numer_domu, numer_mieszkania, 
                kod_pocztowy, miejscowosc, kraj, czy_firma
            });

            fetch(`/dodaj_kontrahenta_ajax/?${params}`)
            .then(handleFetchResponse)
            .then(data => {
                if (data.error) {
                    displayErrorMessage("Błąd przy zapisie kontrahenta: " + data.error);
                } else {
                    // Check if option already exists
                    let optionExists = false;
                    if (kontrahentSelect) {
                        for (let i = 0; i < kontrahentSelect.options.length; i++) {
                            if (kontrahentSelect.options[i].value == data.id) {
                                optionExists = true;
                                break;
                            }
                        }
                        if (!optionExists) {
                            const option = document.createElement("option");
                            option.text = data.nazwa;
                            option.value = data.id;
                            kontrahentSelect.add(option);
                        }
                        kontrahentSelect.value = data.id;
                    }
                    displayErrorMessage("Kontrahent został zapisany.");
                }
            })
            .catch(error => {
                console.error('Błąd:', error);
                displayErrorMessage(`Wystąpił błąd podczas zapisywania kontrahenta: ${error.message}`);
            });
        });
    }

    // -------------------------------------------------------------
    // 6. FIXED: Ukryj rabat functionality
    // -------------------------------------------------------------

    if (ukryjRabatButton) {
        ukryjRabatButton.addEventListener('click', function() {
            // Toggle rabat columns
            document.querySelectorAll('.rabat-col').forEach(col => {
                col.style.display = col.style.display === 'none' ? '' : 'none';
            });

            // Toggle summary rows if they exist
            const sumaPrzedRabatem = document.querySelector('.suma-przed-rabatem');
            const sumaPoRabacie = document.querySelector('.suma-po-rabacie');
            
            if (sumaPrzedRabatem) {
                sumaPrzedRabatem.style.display = sumaPrzedRabatem.style.display === 'none' ? '' : 'none';
            }
            if (sumaPoRabacie) {
                sumaPoRabacie.style.display = sumaPoRabacie.style.display === 'none' ? '' : 'none';
            }
            
            // Update button text
            this.innerText = this.innerText === "Ukryj rabat" ? "Pokaż rabat" : "Ukryj rabat";
            
            updateTotals();
        });
    }

    // -------------------------------------------------------------
    // 7. Notifications handling
    // -------------------------------------------------------------
    
    // Update read status when opening messages
    document.querySelectorAll('.wiadomosc-link').forEach(link => {
        link.addEventListener('click', async function() {
            const wiadomoscId = this.dataset.id;
            if (wiadomoscId) {
                try {
                    await fetch(`/wiadomosci/${wiadomoscId}/oznacz-jako-przeczytana/`);
                } catch (error) {
                    console.error('Error marking message as read:', error);
                }
            }
        });
    });

    console.log('Faktury.js loaded successfully - FIXED VERSION with proper container handling');
});