

// update_quantity.js
document.addEventListener('DOMContentLoaded', function() {
    const quantityInputs = document.querySelectorAll('#quantity-input');
    quantityInputs.forEach(function(input) {
        input.addEventListener('change', updateQuantity);
    });
});

function updateQuantity() {
    const newQuantity = this.value;
    const cartItemId = this.getAttribute('data-cart-item-id');

    // Send AJAX request to update the quantity
    fetch('{% url 'update_cart_item' cart_item_id=${cartItemId}  %}', {
        method: 'POST',
        // `/update-cart-item/${cartItemId}/`
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}' // Include the CSRF token
        },
        body: JSON.stringify({ quantity: newQuantity })
    })
    .then(response => {
        if (response.ok) {
            // Quantity updated successfully
            console.log('Quantity updated');
        } else {
            // Handle error
            console.error('Failed to update quantity');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}