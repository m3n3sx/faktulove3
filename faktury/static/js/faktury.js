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
    
    // Pozycje Faktury
    const ukryjRabatButton = document.querySelector('#ukryj-rabat');
    const addButton = document.querySelector("#add-pozycja");
    const totalForms = document.querySelector("#id_pozycje-TOTAL_FORMS");
    const container = document.querySelector("tbody");
    
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

    // Helper function to create a new row.
    function createRow() {
        const totalFormsElement = document.getElementById('id_pozycje-TOTAL_FORMS');
        const newIndex = parseInt(totalFormsElement.value);
        const emptyFormElement = document.getElementById('empty-form');
        
        if (!emptyFormElement) {
            console.error('Empty form template not found');
            return null;
        }
        
        const emptyForm = emptyFormElement.outerHTML;
        const newRowHTML = emptyForm
            .replace(/__prefix__/g, newIndex)
            .replace(/pozycje-\d+-/g, `pozycje-${newIndex}-`);
      
        const tr = document.createElement('tr');
        tr.classList.add('pozycja-form');
        tr.innerHTML = newRowHTML;
      
        // Inicjalizacja event listeners dla nowego wiersza
        addFormListeners(tr);
        addProduktSelectionListener(tr);
        
        // Dodaj przycisk usuwania
        const deleteBtn = tr.querySelector('.usun-pozycje');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                const deleteCheckbox = tr.querySelector('input[name$="-DELETE"]');
                if (deleteCheckbox) {
                    deleteCheckbox.checked = true;
                    tr.style.display = 'none';
                    updateTotals();
                }
            });
        }
      
        totalFormsElement.value = newIndex + 1;
        return tr;
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
            let newForm = createRow();
            if (!newForm) {
                displayErrorMessage("Nie można utworzyć nowego wiersza");
                return;
            }
            
            container.append(newForm);
            
            // Wyczyść wartości wejściowe w nowym formularzu
            let inputs = newForm.querySelectorAll('input');
            inputs.forEach(input => {
                if (input.type !== 'checkbox') {
                    input.value = '';
                } else {
                    input.checked = false;
                }
            });

            let selects = newForm.querySelectorAll('select');
            selects.forEach(select => {
                select.selectedIndex = 0;
            });

            addFormListeners(newForm);
            addProduktSelectionListener(newForm);
            updateTotals();

        } catch (error) {
            console.error("Error adding position form:", error);
            displayErrorMessage("Wystąpił błąd podczas dodawania pozycji faktury.");
        }
    }

    // FIXED: Dodaje listenery do *pojedynczego* wiersza formularza z prawidłowymi selektorami
    function addFormListeners(form) {
        const fields = [
            'input[name$="ilosc"]',
            'input[name$="cena_netto"]',
            'select[name$="vat"]',  // FIXED: Zmienione z input na select
            'input[name$="rabat"]',
            'select[name$="rabat_typ"]',
        ];

        fields.forEach(selector => {
            const elements = form.querySelectorAll(selector);
            elements.forEach(element => {
                // Usuń istniejące listenery aby uniknąć duplikacji
                element.removeEventListener('change', handleFieldChange);
                element.removeEventListener('keyup', handleFieldChange);
                element.removeEventListener('input', handleFieldChange);
                
                // Dodaj nowe listenery
                element.addEventListener('change', handleFieldChange);
                element.addEventListener('keyup', handleFieldChange);
                element.addEventListener('input', handleFieldChange);  // ADDED: For real-time input
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
        const vatSelect = form.querySelector('select[name$="vat"]');  // FIXED: Zmienione na select
        const jednostkaInput = form.querySelector('input[name$="jednostka"]');
    
        // Remove existing listener to prevent duplicates
        produktSelect.removeEventListener('change', produktSelect._changeHandler);
        
        // Create and store the change handler
        produktSelect._changeHandler = function() {
            const selectedProduktId = this.value;
            if (!selectedProduktId) {
                // Resetowanie pól, jeśli nie wybrano produktu
                if (nazwaInput) nazwaInput.value = '';
                if (cenaNettoInput) cenaNettoInput.value = '';
                if (vatSelect) vatSelect.value = '';
                if (jednostkaInput) jednostkaInput.value = '';
                updateRowValues(null, form);
                return;
            }
    
            // Wyślij zapytanie do API
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
    
                    // Aktualizacja pól formularza
                    if (nazwaInput) nazwaInput.value = data.nazwa || '';
                    if (cenaNettoInput) cenaNettoInput.value = data.cena_netto || '';
                    if (vatSelect) vatSelect.value = data.vat || '';
                    if (jednostkaInput) jednostkaInput.value = data.jednostka || '';
                    
                    // FIXED: Trigger calculation after setting values
                    updateRowValues(null, form);
                })
                .catch(error => {
                    console.error('Błąd:', error);
                    displayErrorMessage(`Wystąpił błąd podczas pobierania danych produktu: ${error.message}`);
                });
        };
        
        produktSelect.addEventListener('change', produktSelect._changeHandler);
    }

    // FIXED: Funkcja pomocnicza do ustawiania wartości pól
    function setFieldValue(form, fieldName, value) {
        const field = form.querySelector(`[name$="${fieldName}"]`);
        if (!field) return;

        if (field.tagName === 'SELECT') {
            field.value = value;
        } else if (field.type === 'checkbox') {
            field.checked = !!value;
        } else {
            field.value = value;
        }
    }

    // FIXED: Improved updateRowValues function with better error handling
    function updateRowValues(event, form) {
        try {
            // Handle case where event is null (when called from product selection)
            const row = event ? event.target.closest('.pozycja-form') : form.closest('.pozycja-form');
            if (!row) return;
            
            // Skip deleted rows
            const deleteInput = row.querySelector('input[type="checkbox"][name$="DELETE"]');
            if (deleteInput && deleteInput.checked) {
                return;
            }
        
            // Get field values with fallbacks
            const iloscInput = row.querySelector('input[name$="ilosc"]');
            const cenaNetto = row.querySelector('input[name$="cena_netto"]');
            const vatSelect = row.querySelector('select[name$="vat"]');  // FIXED: select instead of input
            const rabatInput = row.querySelector('input[name$="rabat"]');
            const rabatTypSelect = row.querySelector('select[name$="rabat_typ"]');
            
            const ilosc = parseFloat(iloscInput?.value) || 0;
            const cena_netto = parseFloat(cenaNetto?.value) || 0;
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
                // Skip deleted rows
                const deleteInput = row.querySelector('input[type="checkbox"][name$="DELETE"]');
                if (deleteInput && deleteInput.checked) {
                    return;
                }

                const iloscInput = row.querySelector('input[name$="ilosc"]');
                const cenaNettoInput = row.querySelector('input[name$="cena_netto"]');
                const rabatInput = row.querySelector('input[name$="rabat"]');
                const rabatTypSelect = row.querySelector('select[name$="rabat_typ"]');
                const vatSelect = row.querySelector('select[name$="vat"]');  // FIXED: select instead of input

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
            addFormListeners(form);
            addProduktSelectionListener(form);
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
    // 6. Ukryj rabat
    // -------------------------------------------------------------

    if (ukryjRabatButton) {
        ukryjRabatButton.addEventListener('click', function() {
            document.querySelectorAll('.rabat-col').forEach(col => {
                col.style.display = col.style.display === 'none' ? '' : 'none';
            });

            const sumaPrzedRabatem = document.querySelector('.suma-przed-rabatem');
            const sumaPoRabacie = document.querySelector('.suma-po-rabacie');
            
            if (sumaPrzedRabatem) {
                sumaPrzedRabatem.style.display = sumaPrzedRabatem.style.display === 'none' ? '' : 'none';
            }
            if (sumaPoRabacie) {
                sumaPoRabacie.style.display = sumaPoRabacie.style.display === 'none' ? '' : 'none';
            }
            
            updateTotals();
            this.innerText = this.innerText === "Ukryj rabat" ? "Pokaż rabat" : "Ukryj rabat";
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

    console.log('Faktury.js loaded successfully - FIXED VERSION');
});