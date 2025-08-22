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

function addProduktSelectionListener(form) {
    const produktSelect = form.querySelector('.produkt-select');
    const jednostkaSelect = form.querySelector('select[name$="jednostka"]');
    const cenaNettoInput = form.querySelector('input[name$="cena_netto"]');
    const vatInput = form.querySelector('input[name$="vat"]');
    const iloscInput = form.querySelector('input[name$="ilosc"]');
    const sumaBruttoInput = form.querySelector('input[name$="suma_brutto"]');
    
    if (!produktSelect || !jednostkaSelect) {
        console.error('Brakujące elementy formularza');
        return;
    }

    produktSelect.addEventListener('change', function() {
        const selectedProduktId = this.value;
        
        if (!selectedProduktId) {
            // Resetowanie pól, jeśli nie wybrano produktu
            if (cenaNettoInput) cenaNettoInput.value = '';
            if (vatInput) vatInput.value = '';
            if (sumaBruttoInput) sumaBruttoInput.value = '';
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
                if (cenaNettoInput) {
                    cenaNettoInput.value = data.cena_netto;
                }
                if (vatInput) {
                    vatInput.value = data.vat === 'zw' ? '0' : data.vat;
                }
                if (jednostkaSelect) {
                    const optionExists = Array.from(jednostkaSelect.options).some(
                        option => option.value === data.jednostka
                    );
                    
                    if (optionExists) {
                        jednostkaSelect.value = data.jednostka;
                    } else {
                        const nowaOpcja = document.createElement('option');
                        nowaOpcja.value = data.jednostka;
                        nowaOpcja.textContent = data.jednostka;
                        jednostkaSelect.add(nowaOpcja);
                        jednostkaSelect.value = data.jednostka;
                    }
                }

                // Obliczenie sumy
                if (iloscInput && sumaBruttoInput) {
                    const ilosc = parseFloat(iloscInput.value) || 0;
                    const cenaNetto = parseFloat(cenaNettoInput.value) || 0;
                    const vat = parseFloat(vatInput.value) || 0;
                    
                    const sumaNetto = ilosc * cenaNetto;
                    const sumaBrutto = sumaNetto * (1 + vat / 100);
                    
                    sumaBruttoInput.value = sumaBrutto.toFixed(2);
                }

                updateRowValues(null, form);
            })
            .catch(error => {
                console.error('Błąd:', error);
                displayErrorMessage(`Wystąpił błąd podczas pobierania danych produktu: ${error.message}`);
            });
    });
}