const cartIcon = document.querySelector('.cart-icon');
const addToCartButtons = document.querySelectorAll('.add-to-cart');
let cart = [];

// Add to cart functionality
// addToCartButtons.forEach((button) => {
//     button.addEventListener('click', (event) => {
//         const movieTitle = event.target.parentNode.querySelector('h3').textContent;
//         addToCart(movieTitle);
//     });
// });

// function addToCart(movieTitle) {
//     if (!cart.includes(movieTitle)) {
//         cart.push(movieTitle);
//         updateCartIcon();
//         console.log(`Added ${movieTitle} to the cart.`);
//     } else {
//         console.log(`${movieTitle} is already in the cart.`);
//     }
// }

function updateCartIcon() {
    cartIcon.textContent = `Cart (${cart.length})`;
}

// Auto-sliding functionality
const slides = document.querySelectorAll('.banner-slide');
const prevButton = document.querySelector('.prev');
const nextButton = document.querySelector('.next');
let currentSlide = 0;
let slideInterval;

// Function to show the current slide
function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.style.display = i === index ? 'block' : 'none';
    });
}

// Show the first slide initially
showSlide(currentSlide);

// Auto-slide logic
function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(currentSlide);
}

// Add event listeners for navigation buttons
nextButton.addEventListener('click', () => {
    clearInterval(slideInterval); // Pause auto-sliding on manual navigation
    nextSlide();
    startAutoSlide();
});

prevButton.addEventListener('click', () => {
    clearInterval(slideInterval); // Pause auto-sliding on manual navigation
    prevSlide();
    startAutoSlide();
});

// Start auto-sliding
function startAutoSlide() {
    slideInterval = setInterval(nextSlide, 5000); // Change slide every 5 seconds
}

// Stop auto-sliding
function stopAutoSlide() {
    clearInterval(slideInterval);
}

// Function to update the main image when a thumbnail is clicked
function updateMainImage(thumbnail) {
    // Get the main image element
    const mainImage = document.getElementById('mainImage');
    
    // Update the main image source to the clicked thumbnail's source
    mainImage.src = thumbnail.src;
    
    // Remove 'active' class from all thumbnails
    const thumbnails = document.querySelectorAll('.thumbnail');
    thumbnails.forEach(th => th.classList.remove('active'));

    // Add 'active' class to the clicked thumbnail
    thumbnail.classList.add('active');
}

function updateQuantity(change) {
    const input = document.getElementById('quantity');
    const newValue = parseInt(input.value) + change;
    if (newValue >= 1) {
        input.value = newValue;
    }
}

// // Function to show the cart and add products
// function addToCart(button) {
//     // Get productId from the button's data attribute
//     const productId = button.getAttribute('data-product-id');

//     // Get selected size
//     const sizeSelect = document.getElementById('size');
//     const size = sizeSelect ? sizeSelect.value : null;

//     // Get selected color
//     const colorSelect = document.getElementById('color');
//     const color = colorSelect ? colorSelect.value : null;

//     // Get quantity
//     const quantityInput = document.getElementById('quantity');
//     const quantity = quantityInput ? parseInt(quantityInput.value, 10) : 1;

//     // Validate required fields
//     if (!productId) {
//         alert('Product ID is missing!');
//         return;
//     }
//     if (sizeSelect && !size) {
//         alert('Please select a size!');
//         return;
//     }
//     if (colorSelect && !color) {
//         alert('Please select a color!');
//         return;
//     }

//     // Create the data object
//     const data = {
//         productId,
//         quantity,
//         size: size || 'none', // Default to 'none' if no size is available
//         color: color || 'none' // Default to 'none' if no color is available
//     };

//     console.log('Data to send:', data);

//     // Send the data to the server via fetch
//     fetch('/add-to-cart', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(data)
//     })
//         .then(response => response.json())
//         .then(result => {
//             if (result.error) {
//                 alert('Error: ' + result.error);
//             } else {
//                 // Display success message
//                 // alert('Item added to cart!');
//                 console.log(result);
    
//                 // Call the `/get-cart` endpoint to fetch updated cart details
//                 fetch('/get-cart', {
//                     method: 'GET',
//                     headers: {
//                         'Content-Type': 'application/json'
//                     }
//                 })
//                 .then(response => response.json())
//                 .then(cartResult => {
//                     if (cartResult.error) {
//                         alert('Error fetching cart: ' + cartResult.error);
//                     } else {
//                         // Handle the updated cart data
//                         console.log('Updated Cart:', cartResult);
    
//                         // For example, update the cart UI with the updated items
//                         updateCartUI(cartResult.cartItems, cartResult.total);
//                     }
//                 })
//                 .catch(error => {
//                     console.error('Error fetching updated cart:', error);
//                     alert('An error occurred while fetching the cart.');
//                 });
//             }
//         })
//         .catch(error => {
//             console.error('Error adding to cart:', error);
//             alert('An error occurred while adding to the cart.');
//         });
    
// }

// Function to add products to the cart and redirect to the cart page
function addToCart(button) {
    // Get productId from the button's data attribute
    const productId = button.getAttribute('data-product-id');

    // Get selected size
    const sizeSelect = document.getElementById('size');
    const size = sizeSelect ? sizeSelect.value : null;

    // Get selected color
    const colorSelect = document.getElementById('color');
    const color = colorSelect ? colorSelect.value : null;

    // Get quantity
    const quantityInput = document.getElementById('quantity');
    const quantity = quantityInput && quantityInput.value > 0 ? parseInt(quantityInput.value, 10) : 1;

    const isCartUpdate = document.getElementById('isCartUpdate');
    const old_color = document.getElementById('old_color');
    const old_size = document.getElementById('old_size');

    // Validate required fields
    if (!productId) {
        alert('Product ID is missing!');
        return;
    }
    if (sizeSelect && !size) {
        alert('Please select a size!');
        return;
    }
    if (colorSelect && !color) {
        alert('Please select a color!');
        return;
    }

    // Create the data object
    const data = {
        productId,
        quantity,
        size: size || 'none', // Default to 'none' if no size is available
        color: color || 'none', // Default to 'none' if no color is available
        isCartUpdate,
        old_color,
        old_size
    };

    // Send the data to the server via fetch
    fetch('/add-to-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.error) {
                alert('Error: ' + result.error);
            } else {
                // Fetch and display the updated cart
                fetch('/get-cart-list', {
                    method: 'GET',
                })
                    .then(response => {
                        if (!response.ok) throw new Error('Failed to fetch cart HTML.');
                        return response.text();
                    })
                    .then(html => {
                        // Inject the cart HTML content into the page
                        const cartContainer = document.getElementById('cart-list-content');
                        cartContainer.innerHTML = html;

                        // Show the cart list by sliding it in
                        document.getElementById('cart-list-container').classList.add('show');
                    })
                    .catch(error => console.error('Error loading cart:', error));
            }
        })
        .catch(error => {
            console.error('Error adding to cart:', error);
            alert('An error occurred while adding to the cart.');
        });
}



// Function to add products to the cart and dynamically update the cart content
function GetCart(button) {
    //const productId = button.getAttribute('data-product-id');
    const productId ='123456'
    
  console.log(`Product with ID ${productId} added to cart.`);

  // Create an object to send to the backend (e.g., current cart items or product ID)
  const cartData = {
    productId: productId,
    // You can include other cart data like quantities if needed
  };

  // Send a POST request to the server to get cart-list.html
  fetch('/get-cart-list', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ cartData: cartData }),
  })
  .then(response => response.text())
  .then(html => {
    // Inject the cart HTML content into the page
    const cartContainer = document.getElementById('cart-list-content');
    cartContainer.innerHTML = html;

    // Optionally, display the cart list by sliding it in from the right
    document.getElementById('cart-list-container').classList.add('show');
  })
  .catch(error => console.error('Error loading cart:', error));
}

function closeCartList() {
  document.getElementById('cart-list-container').classList.remove('show');
  }
function GetCart() {
console.log('Fetching cart list...');

// Send a simple GET request
fetch('/get-cart-list', {
    method: 'GET',
})
    .then(response => {
    if (!response.ok) throw new Error('Failed to fetch cart HTML.');
    return response.text();
    })
    .then(html => {
    // Inject the cart HTML content into the page
    const cartContainer = document.getElementById('cart-list-content');
    cartContainer.innerHTML = html;

    // Show the cart list by sliding it in
    document.getElementById('cart-list-container').classList.add('show');
    })
    .catch(error => console.error('Error loading cart:', error));
}

function loadCartContent(productId) {
// Dynamically load the content into the cart (for example, product details)
const cartContent = document.getElementById('cart-list-content');
const cartItem = `
    <ul>
    <li>Product ID: ${productId}</li>
    </ul>
`;
cartContent.innerHTML += cartItem;
}

function closeCartList() {
document.getElementById('cart-list-container').classList.remove('show');
}
    

// Function to close the cart when the user clicks "close"
function closeCartList() {
  document.getElementById('cart-list-container').classList.remove('show');
}


  
// Function to close the cart when the user clicks "close"
function closeCartList() {
document.getElementById('cart-list-container').classList.remove('show');
}
  

// Handle updating the cart
document.getElementById('update-cart').addEventListener('click', async () => {
    const cartData = [];
    document.querySelectorAll('.quantity-input').forEach(input => {
        cartData.push({
            prodId: input.getAttribute('data-prod-id'),
            quantity: input.value,
        });
    });

    try {
        const response = await fetch('/update-cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(cartData),
        });

        if (response.ok) {
            alert('Cart updated successfully!');
            location.reload();
        } else {
            alert('Failed to update the cart.');
        }
    } catch (error) {
        console.error(error);
        alert('An error occurred while updating the cart.');
    }
});


function updateQty(itemId, change) {
    const inputField = document.getElementById(`quantity-${itemId}`);
    let currentValue = parseInt(inputField.value) || 1;

    // Update the value, ensuring it doesn't go below 1
    const newValue = Math.max(1, currentValue + change);
    inputField.value = newValue;
}

document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners to quantity inputs
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', (e) => {
            const productId = e.target.id.split('-')[1]; // Extract product ID from input ID
            const newQuantity = e.target.value;

            // Create a new XMLHttpRequest to send form data
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/update-cart', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

            // Define the data to send (URL encoded)
            const params = `productId=${encodeURIComponent(productId)}&newQuantity=${encodeURIComponent(newQuantity)}`;

            // Send the data
            xhr.send(params);

            xhr.onload = function () {
                if (xhr.status === 200) {
                    console.log('Success:', xhr.responseText);
                } else {
                    console.error('Error:', xhr.responseText);
                }
            };
        });
    });
});



// Start auto-sliding when the page loads
startAutoSlide();
