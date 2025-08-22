document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    var calendar = new tui.Calendar(calendarEl, { // WAŻNE: tui.Calendar z wielkiej litery
      defaultView: 'month',
      taskView: true,
      scheduleView: true,
      useDetailPopup: true,
      // ... inne opcje ...
    });

    // Pobierz dane z widoku Django
    const calendarContainer = document.getElementById('calendar'); // Poprawione ID!
    const url = calendarContainer.dataset.url; // Pobierz URL z atrybutu data-url
    console.log("URL do pobrania danych:", url); // Dodaj to!

        
    fetch(url)  // Użyj zmiennej url!
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(events => {
            calendar.createSchedules(events);
        })
        .catch(error => {
            console.error('Błąd pobierania danych kalendarza:', error);
            calendarContainer.innerHTML = '<p>Wystąpił błąd podczas ładowania kalendarza.</p>'; //Komunikat dla uzytkownika
        });

    // Przyciski do zmiany widoku (opcjonalnie - dodaj do HTML, jeśli chcesz)
    // Te przyciski muszą mieć id prev-month i next-month. Upewnij się, że masz je w HTML.
     document.getElementById('prev-month')?.addEventListener('click', function() { // Użyj ?. (optional chaining)
       calendar.prev();
     });
    document.getElementById('next-month')?.addEventListener('click', function() { // Użyj ?.
        calendar.next();
    });
});
