document.addEventListener('DOMContentLoaded', function() {
    // Dane do kalendarza (przekazane z Django)
    let faktury;
    try {
        faktury = JSON.parse(document.getElementById('faktury-data').textContent);  // WAŻNE: użyj |safe, bo to dane JSON
    } catch (e) {
        console.error('Error parsing faktury data:', e);
        faktury = [];
    }
    let zadania;
    try {
        zadania = JSON.parse(document.getElementById('zadania-data').textContent);
    } catch (e) {
        console.error('Error parsing zadania data:', e);
        zadania = [];
    }
    let currentYear = JSON.parse(document.getElementById('current-year').textContent);
    let currentMonth = JSON.parse(document.getElementById('current-month').textContent); // Miesiące w JS są od 0 do 11!
    const today = new Date (JSON.parse(document.getElementById('today').textContent));
   
    // Funkcja do generowania kalendarza
        function generateCalendar(year, month, faktury, zadania) {
            const firstDay = new Date(year, month - 1, 1); // Miesiące 0-11
            const lastDay = new Date(year, month, 0);
            const startDayOfWeek = firstDay.getDay(); // 0 (niedziela) do 6 (sobota)
            const numDays = lastDay.getDate();
   
            let calendarHTML = '<table class="table table-bordered">';
            calendarHTML += '<thead><tr><th colspan="7">' + year + '-' + String(month).padStart(2, '0') + '</th></tr>';
            calendarHTML += '<tr><th>Nd</th><th>Pn</th><th>Wt</th><th>Śr</th><th>Cz</th><th>Pt</th><th>So</th></tr></thead>';
            calendarHTML += '<tbody>';
   
            let day = 1;
            let startDay = (startDayOfWeek === 0) ? 6 : startDayOfWeek - 1;// Tydzień zaczynamy od poniedziałku, więc przesuwamy
   
            for (let i = 0; i < 6; i++) { // Max 6 tygodni w miesiącu
                calendarHTML += '<tr>';
                for (let j = 0; j < 7; j++) {
                    if (i === 0 && j < startDay) {
                        calendarHTML += '<td></td>'; // Puste komórki przed pierwszym dniem miesiąca
                    } else if (day <= numDays) {
                        let cellContent = `<span>${day}</span>`;
                        // Dodaj zdarzenia dla faktur
                        for(const faktura of faktury){
                            let fakturaDate = new Date(faktura.termin_platnosci);
                            if (fakturaDate.getFullYear() === year && fakturaDate.getMonth() === month -1 && fakturaDate.getDate() === day) {
                                // Prosta wizualizacja - dodajemy link
                                 if (faktura.typ_faktury == 'sprzedaz'){
                                    cellContent += `<br><a href="${faktura.url}" style="color: blue;">Faktura Sprzedaż: ${faktura.numer}</a>`;
                                }
                                else{
                                    cellContent += `<br><a href="${faktura.url}" style="color: red;">Faktura Koszt: ${faktura.numer}</a>`;
                                }
   
                            }
                        }
                        //Dodaj zadania
                         for(const zadanie of zadania){
                            let zadanieDate = new Date(zadanie.termin_wykonania);
                            if (zadanieDate.getFullYear() === year && zadanieDate.getMonth() === month -1 && zadanieDate.getDate() === day) {
                                 cellContent += `<br><a href="${zadanie.url}" style="color: green;">Zadanie: ${zadanie.tytul}</a>`;
                            }
                        }
                        calendarHTML += `<td>${cellContent}</td>`;
                        day++;
                    } else {
                        calendarHTML += '<td></td>'; // Puste komórki po ostatnim dniu miesiąca
                    }
                }
                calendarHTML += '</tr>';
                if (day > numDays) {
                    break; // Jeśli doszliśmy do końca miesiąca, przerwij pętlę
                }
            }
   
            calendarHTML += '</tbody></table>';
            return calendarHTML;
        }
   
    // Wygeneruj kalendarz dla bieżącego miesiąca
    const calendarContainer = document.getElementById('calendar-container');
    calendarContainer.innerHTML = generateCalendar(currentYear, currentMonth, faktury, zadania);
      // Dodaj obsługę przycisków nawigacji
    document.getElementById('prev-month').addEventListener('click', function() {
        currentMonth--;
        if (currentMonth < 1) {
            currentMonth = 12;
            currentYear--;
        }
        calendarContainer.innerHTML = generateCalendar(currentYear, currentMonth, faktury, zadania); //Przerysowujemy kalendarz
    });
   
    document.getElementById('next-month').addEventListener('click', function() {
        currentMonth++;
        if (currentMonth > 12) {
            currentMonth = 1;
            currentYear++;
        }
        calendarContainer.innerHTML = generateCalendar(currentYear, currentMonth, faktury, zadania); //Przerysowujemy kalendarz
    });
   });