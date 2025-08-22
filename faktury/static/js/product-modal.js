document.addEventListener("DOMContentLoaded", function() {
    // Get references to modal elements
    const saveProductButton = document.getElementById('zapisz-produkt');
    const productForm = document.getElementById('dodaj-produkt-form');
    const productModal = document.getElementById('dodajProduktModal');
    
    // Add event listener for the save button if it exists
    if (saveProductButton && productForm) {
        saveProductButton.addEventListener('click', function() {
            // Get form data
            const formData = new FormData(productForm);
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Send AJAX request
            fetch(productForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Add the new product to all product selection dropdowns
                    document.querySelectorAll('.produkt-select').forEach(select => {
                        const option = document.createElement('option');
                        option.value = data.id;
                        option.textContent = data.nazwa;
                        select.appendChild(option);
                    });
                    
                    // Close the modal
                    const modalInstance = bootstrap.Modal.getInstance(productModal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                    
                    // Reset the form
                    productForm.reset();
                    
                    // Show success message
                    alert('Produkt został dodany pomyślnie');
                } else {
                    // Show error message
                    alert('Błąd podczas dodawania produktu: ' + data.errors);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Wystąpił błąd podczas dodawania produktu');
            });
        });
    }
});