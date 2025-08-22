document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("pobierz-dane-gus").addEventListener("click", function() {
        let nip = document.getElementById("id_nabywca_nip").value;

        fetch(`/api/get-company-data/?nip=${nip}`)
            .then(response => response.json())
            .then(data => {
                if (!data.error) {
                    document.getElementById("id_nabywca_nazwa").value = data.data.Nazwa;
                    document.getElementById("id_nabywca_ulica").value = data.data.Ulica;
                    document.getElementById("id_nabywca_kod_pocztowy").value = data.data.KodPocztowy;
                    document.getElementById("id_nabywca_miejscowosc").value = data.data.Miejscowosc;
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error("Błąd:", error));
    });
});

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

    document.addEventListener("DOMContentLoaded", function() {
        document.getElementById("pobierz-dane-gus").addEventListener("click", function() {
            let nip = document.getElementById("id_nabywca_nip").value;
    
            fetch(`/pobierz_dane_z_gus/?nip=${nip}`) // Poprawiony URL
                .then(response => response.json())
                .then(data => {
                    if (!data.error) {
                        document.getElementById("id_nabywca_nazwa").value = data.data.Nazwa;
                        document.getElementById("id_nabywca_ulica").value = data.data.Ulica;
                        document.getElementById("id_nabywca_kod_pocztowy").value = data.data.KodPocztowy;
                        document.getElementById("id_nabywca_miejscowosc").value = data.data.Miejscowosc;
                    } else {
                        alert(data.error);
                    }
                })
                .catch(error => console.error("Błąd:", error));
        });
    });


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
                    nazwaInput.value = data.nazwa;
                    ulicaInput.value = data.ulica;
                    numerDomuInput.value = data.numer_domu;
                    numerMieszkaniaInput.value = data.numer_mieszkania || '';
                    kodPocztowyInput.value = data.kod_pocztowy;
                    miejscowoscInput.value = data.miejscowosc;
                    nipInput.value = data.nip;
                    krajInput.value = data.kraj;

                    if (data.czy_firma) {
                        firmaRadio.checked = true;
                    } else {
                        osobaPrywatnaRadio.checked = true;
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
// Pobierz pusty formularz (jako string)
    const emptyForm = document.querySelector('#empty-form').outerHTML;
  // Helper function to create a new row.
  function createRow() {
    const totalForms = document.getElementById('id_pozycje-TOTAL_FORMS');
    const newIndex = parseInt(totalForms.value);
    const emptyForm = document.getElementById('empty-form').outerHTML;
  
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
    deleteBtn.addEventListener('click', function() {
      const deleteCheckbox = tr.querySelector('input[name$="-DELETE"]');
      deleteCheckbox.checked = true;
      tr.style.display = 'none';
      updateTotals();
    });
  
    totalForms.value = newIndex + 1;
    return tr;
  }

    // -------------------------------------------------------------
    // 3. Obsługa dodawania pozycji faktury (i obliczeń)
    // -------------------------------------------------------------

    if (addButton && container) { //Najpierw sprawdź czy istnieją.
        addButton.addEventListener('click', addPozycjaForm);

        // Delegacja zdarzeń dla przycisków usuwania (istniejące wiersze). Użyj delegacji.
        container.addEventListener('click', function(event) {
            if (event.target.classList.contains('usun-pozycje')) {
                const row = event.target.closest('.pozycja-form');
                // Oznacz do usunięcia, zamiast od razu usuwać
                const deleteInput = row.querySelector('input[type="checkbox"][name$="DELETE"]');
                if (deleteInput) {
                    deleteInput.checked = true;
                }
                row.style.display = 'none'; // Ukryj wiersz
                updateTotals();
            }
        });
    }

    function addPozycjaForm() {
        try {
           let newForm = createRow();
            container.append(newForm); //Dodaj na końcu.
            // Wyczyść wartości wejściowe w nowym formularzu.
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

            addFormListeners(newForm);        // Dodaj listenery do *nowego* formularza
            addProduktSelectionListener(newForm); // Dodaj listener *po* dodaniu wiersza i wyczyszczeniu pól
            updateTotals();                   // Przelicz sumy

        } catch (error) {
            console.error("Error adding position form:", error);
            displayErrorMessage("Wystąpił błąd podczas dodawania pozycji faktury.");
        }
    }


    // Dodaje listenery do *pojedynczego* wiersza formularza
    function addFormListeners(form) {
        const fields = [
            'input[name$="ilosc"]',
            'input[name$="cena_netto"]',
            'select[name$="vat"]',
            'input[name$="rabat"]',
            'select[name$="rabat_typ"]',
        ];

        fields.forEach(selector => {
            const elements = form.querySelectorAll(selector);
            elements.forEach(element => {
                // Użyj nazwanej funkcji, aby można było łatwo usunąć listener w razie potrzeby.
                const listener = function(event) { updateRowValues(event, form); };
                element.addEventListener('change', listener);
                element.addEventListener('keyup', listener); // Dla pól tekstowych (np. ilosc, cena)
            });
        });
    }

    // Dodaje listener zmiany wyboru produktu do *pojedynczego* wiersza formularza
    function addProduktSelectionListener(form) {
        const produktSelect = form.querySelector('.produkt-select');
        const nazwaInput = form.querySelector('input[name$="nazwa"]');
        const cenaNettoInput = form.querySelector('input[name$="cena_netto"]');
        const vatInput = form.querySelector('input[name$="vat"]');
        const jednostkaInput = form.querySelector('input[name$="jednostka"]');
    
        produktSelect.addEventListener('change', function() {
            const selectedProduktId = this.value;
            if (!selectedProduktId) {
                // Resetowanie pól, jeśli nie wybrano produktu
                nazwaInput.value = '';
                cenaNettoInput.value = '';
                vatInput.value = '';
                jednostkaInput.value = '';
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
                    nazwaInput.value = data.nazwa;
                    cenaNettoInput.value = data.cena_netto;
                    vatInput.value = data.vat;
                    jednostkaInput.value = data.jednostka;
                });
        });
    }
    // Funkcja pomocnicza do ustawiania wartości pól, obsługująca różne typy inputów
    function setFieldValue(form, fieldName, value) {
        const field = form.querySelector(`[name$="${fieldName}"]`);
        if (!field) return; // Wyjdź, jeśli pole nie zostanie znalezione

        if (field.tagName === 'SELECT') {
            field.value = value; //Ustaw value dla select
        } else if (field.type === 'checkbox') {
            field.checked = !!value;  // Konwertuj na boolean dla checkbox-ów
        } else {
            field.value = value;  // Ustaw value dla inputów
        }
    }


    function updateRowValues(event, form) {
        // Handle case where event is null (when called from product selection)
        const row = event ? event.target.closest('.pozycja-form') : form.closest('.pozycja-form');
        if (!row) return;
        
        // Rest of the function remains the same
        const deleteInput = row.querySelector('input[type="checkbox"][name$="DELETE"]');
        if (deleteInput && deleteInput.checked) {
            return;
        }
    
        const ilosc = parseFloat(row.querySelector('input[name$="ilosc"]').value) || 0;
        const cena_netto = parseFloat(row.querySelector('input[name$="cena_netto"]').value) || 0;
        const vatSelect = row.querySelector('select[name$="vat"]');
        const vat = vatSelect.value === 'zw' ? 0 : parseFloat(vatSelect.value) || 0;
        const rabat = parseFloat(row.querySelector('input[name$="rabat"]').value) || 0;
        const rabat_typ = row.querySelector('select[name$="rabat_typ"]').value;
    
        let wartosc_netto = ilosc * cena_netto;
        if (rabat_typ === 'procent' && rabat > 0) {
            wartosc_netto = wartosc_netto * (1 - rabat / 100);
        } else if (rabat_typ === 'kwota' && rabat > 0) {
            wartosc_netto = wartosc_netto - rabat;
        }
    
        wartosc_netto = parseFloat(wartosc_netto.toFixed(2));
        const wartosc_vat = wartosc_netto * (vat / 100);
        const wartosc_brutto = wartosc_netto + wartosc_vat;
    
        row.querySelector('.wartosc-netto-col').textContent = wartosc_netto.toFixed(2);
        row.querySelector('.wartosc-brutto-col').textContent = wartosc_brutto.toFixed(2);
    
        updateTotals();
    }


    function updateTotals() {
     try{
        let sumaNettoPrzedRabatem = 0;
        let sumaRabatow = 0;
        let sumaNettoPoRabacie = 0;
        let sumaVat = 0;
        let sumaBrutto = 0;


        document.querySelectorAll('.pozycja-form').forEach(row => {
            // Pomiń usuwane wiersze (te z zaznaczonym checkboxem DELETE)
            const deleteInput = row.querySelector('input[type="checkbox"][name$="DELETE"]');
            if (deleteInput && deleteInput.checked) {
                return; // Pomiń ten wiersz
            }

            const ilosc = parseFloat(row.querySelector('input[name$="ilosc"]').value) || 0;
            const cena_netto = parseFloat(row.querySelector('input[name$="cena_netto"]').value) || 0;
            const rabat = parseFloat(row.querySelector('input[name$="rabat"]').value) || 0;
            const rabat_typ = row.querySelector('select[name$="rabat_typ"]').value;
            const vatSelect = row.querySelector('select[name$="vat"]');
            const vat = vatSelect.value === 'zw' ? 0 : parseFloat(vatSelect.value) || 0;

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
            wartosc_netto = parseFloat(wartosc_netto.toFixed(2));  // Zaokrąglaj *po* uwzględnieniu rabatu
            sumaNettoPoRabacie += wartosc_netto;
            let wartosc_vat = wartosc_netto * (vat / 100);
            sumaVat += wartosc_vat
            sumaBrutto += wartosc_netto + wartosc_vat; // Poprawiony wzór (uwzględnia już rabat)

        });

        document.querySelector('.suma-netto-przed-rabatem').textContent = sumaNettoPrzedRabatem.toFixed(2);
        document.querySelector('.suma-rabatu').textContent = sumaRabatow.toFixed(2);
        document.querySelector('.suma-netto-po-rabacie').textContent = sumaNettoPoRabacie.toFixed(2);
        document.querySelector('.suma-vat').textContent = sumaVat.toFixed(2);
        document.querySelector('.suma-brutto').textContent = sumaBrutto.toFixed(2);
    }catch (error) {
            console.error("Błąd podczas aktualizacji sum:", error);
            displayErrorMessage("Wystąpił błąd podczas obliczania sum.");
        }

    }

    // --- Inicjalizacja (po załadowaniu DOM) ---
    // Dodaj listenery do *istniejących* formularzy.  To MUSI być zrobione *po* zdefiniowaniu funkcji.
    if (pozycjaForm.length > 0) { // Sprawdź, czy są jakieś początkowe formularze
        pozycjaForm.forEach(form => {
            addFormListeners(form);          // Dodaj listenery do pól
            addProduktSelectionListener(form); // Dodaj listener do pola wyboru produktu
        });
        updateTotals();  // Oblicz sumy początkowe
    }


    // -------------------------------------------------------------
    // 4. Obsługa radio buttonów Firma/Osoba prywatna
    // -------------------------------------------------------------

    function toggleNipField() {
        if (osobaPrywatnaRadio.checked) {
            nipInput.value = '';
            nipInput.disabled = true;
            nipInput.style.display = 'none';
            if (pobierzDaneGUSButton) {
                pobierzDaneGUSButton.disabled = true;
                pobierzDaneGUSButton.style.display = 'none';
            }
        } else {
            nipInput.disabled = false;
            nipInput.style.display = 'block';
            if (pobierzDaneGUSButton) {
                pobierzDaneGUSButton.disabled = false;
                pobierzDaneGUSButton.style.display = 'block';
            }
        }
    }

    if (firmaRadio && osobaPrywatnaRadio) {
        firmaRadio.addEventListener('change', toggleNipField);
        osobaPrywatnaRadio.addEventListener('change', toggleNipField);
        toggleNipField(); // Wywołaj przy załadowaniu strony, aby ustawić początkowy stan.
    }


    // -------------------------------------------------------------
    // 5. Obsługa zapisu kontrahenta
    // -------------------------------------------------------------

    if (saveButton) {
        saveButton.addEventListener('click', function() {
            const nip = nipInput.value;
            const nazwa = nazwaInput.value;
            const ulica = ulicaInput.value;
            const numer_domu = numerDomuInput.value;
            const numer_mieszkania = numerMieszkaniaInput.value;
            const kod_pocztowy = kodPocztowyInput.value;
            const miejscowosc = miejscowoscInput.value;
            const kraj = krajInput.value;
            const czy_firma = firmaRadio.checked;

            if (!nazwa || (czy_firma && !nip) || !ulica || !numer_domu || !kod_pocztowy || !miejscowosc) {
                displayErrorMessage('Wypełnij wszystkie wymagane pola (dla firmy: Nazwa, NIP, Ulica, Numer domu, Kod pocztowy, Miejscowość; dla osoby prywatnej: Nazwa, Ulica, Numer domu, Kod pocztowy, Miejscowość).');
                return;
            }

            fetch(`/dodaj_kontrahenta_ajax/?nip=${nip}&nazwa=${nazwa}&ulica=${ulica}&numer_domu=${numer_domu}&numer_mieszkania=${numer_mieszkania}&kod_pocztowy=${kod_pocztowy}&miejscowosc=${miejscowosc}&kraj=${kraj}&czy_firma=${czy_firma}`)
            .then(handleFetchResponse)
            .then(data => {
                if (data.error) {
                    displayErrorMessage("Błąd przy zapisie kontrahenta: " + data.error);
                } else {
                    let optionExists = false;
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
    // 6.  Ukryj rabat
    // -------------------------------------------------------------

    if (ukryjRabatButton) {
        ukryjRabatButton.addEventListener('click', function() {
            document.querySelectorAll('.rabat-col').forEach(col => {
                col.style.display = col.style.display === 'none' ? '' : 'none';
            });

            document.querySelector('.suma-przed-rabatem').style.display = document.querySelector('.suma-przed-rabatem').style.display === 'none' ? '' : 'none';
            document.querySelector('.suma-po-rabacie').style.display = document.querySelector('.suma-po-rabacie').style.display === 'none' ? '' : 'none';
            updateTotals();

            this.innerText = this.innerText === "Ukryj rabat" ? "Pokaż rabat" : "Ukryj rabat";

        });
    }


// Aktualizacja stanu przeczytania przy otwarciu wiadomości
document.querySelectorAll('.wiadomosc-link').forEach(link => {
    link.addEventListener('click', async function() {
        const wiadomoscId = this.dataset.id;
        await fetch(`/wiadomosci/${wiadomoscId}/oznacz-jako-przeczytana/`);
    });
});

});