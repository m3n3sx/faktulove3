// Funkcja do pobrania wartości ciasteczka na podstawie jego nazwy
function getCookie(name) {
    let cookieArr = document.cookie.split(';');
  
    // Przeszukaj ciasteczka
    for (let i = 0; i < cookieArr.length; i++) {
        let cookie = cookieArr[i].trim();
      
        // Jeśli znaleziono ciasteczko, które zaczyna się od podanej nazwy
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1); // Zwróć wartość ciasteczka
        }
    }
    return null; // Jeśli nie znaleziono ciasteczka
}


document.addEventListener('DOMContentLoaded', function() {
    // Funkcja do ładowania powiadomień
    function loadNotifications() {
        fetch('/notifications/json/')
            .then(response => response.json())
            .then(data => {
                const newNotificationsDiv = document.getElementById('new-notifications');
                newNotificationsDiv.innerHTML = ''; // Wyczyść istniejące powiadomienia
                
                data.forEach(notification => {
                    const notificationHtml = `
                        <a href="javascript:void(0)" class="px-24 py-12 d-flex align-items-start gap-3 mb-2 justify-content-between ${notification.is_read ? 'bg-neutral-50' : ''}" data-id="${notification.id}">
                            <div class="text-black hover-bg-transparent hover-text-primary d-flex align-items-center gap-3"> 
                                <span class="w-44-px h-44-px ${notification.iconClass || 'bg-success-subtle'} text-info-main rounded-circle d-flex justify-content-center align-items-center flex-shrink-0">
                                    FV
                                </span> 
                                <div>
                                    <h6 class="text-md fw-semibold mb-4">${notification.title}</h6>
                                    <p class="mb-0 text-sm text-secondary-light text-w-200-px">${notification.timestamp}</p>
                                </div>
                            </div>
                            <button class="btn btn-sm btn-outline-primary mark-as-read" data-id="${notification.id}" style="margin-left: 10px;">✔</button>
                        </a>
                    `;
                    newNotificationsDiv.insertAdjacentHTML('beforeend', notificationHtml);
                });
            })
            .catch(error => console.error('Error loading notifications:', error));
    }
    
    // Załaduj powiadomienia przy starcie
    loadNotifications();

    // Obsługa zdarzenia click dla przycisku "Oznacz jako przeczytane"
    document.addEventListener('click', function(event) {
        const markAsReadButton = event.target.closest('.mark-as-read');

        // Jeśli kliknięto przycisk oznaczenia jako przeczytane
        if (markAsReadButton) {
            const notificationId = markAsReadButton.dataset.id;
            
            fetch(`/notifications/${notificationId}/mark-as-read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    // Odśwież listę powiadomień
                    loadNotifications();
                }
            })
            .catch(error => console.error('Error marking notification as read:', error));
        }
    });
});
