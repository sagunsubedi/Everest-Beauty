// Everest Beauty - Main JavaScript

// Global variables
let cartCount = 0;
let wishlistItems = [];

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.custom-notification');
    existingNotifications.forEach(notification => notification.remove());

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `custom-notification alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            <span>${message}</span>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

function updateCartCount(count) {
    const cartBadge = document.querySelector('.fa-shopping-cart + .badge');
    if (cartBadge) {
        cartBadge.textContent = count;
    }
    cartCount = count;
}

function updateWishlistCount(count) {
    const wishlistBadge = document.querySelector('.fa-heart + .badge');
    if (wishlistBadge) {
        wishlistBadge.textContent = count;
    }
}

// Cart functionality
function addToCart(productId, quantity = 1) {
    const button = document.querySelector(`[data-product-id="${productId}"]`);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner"></span> Adding...';
    }

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
        },
        body: `quantity=${quantity}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_count);
            showNotification(data.message, 'success');
            
            // Update button state
            if (button) {
                button.innerHTML = '<i class="fas fa-check"></i> Added!';
                setTimeout(() => {
                    button.disabled = false;
                    button.innerHTML = 'Add to Cart';
                }, 2000);
            }
        } else {
            showNotification(data.message || 'Error adding product to cart', 'error');
            if (button) {
                button.disabled = false;
                button.innerHTML = 'Add to Cart';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding product to cart', 'error');
        if (button) {
            button.disabled = false;
            button.innerHTML = 'Add to Cart';
        }
    });
}

function removeFromCart(itemId) {
    if (confirm('Are you sure you want to remove this item from your cart?')) {
        fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        })
        .then(response => {
            if (response.ok) {
                // Remove item from DOM
                const cartItem = document.querySelector(`[data-cart-item-id="${itemId}"]`);
                if (cartItem) {
                    cartItem.remove();
                }
                showNotification('Item removed from cart', 'success');
                updateCartTotal();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error removing item from cart', 'error');
        });
    }
}

function updateCartItemQuantity(itemId, quantity) {
    if (quantity <= 0) {
        removeFromCart(itemId);
        return;
    }

    fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `quantity=${quantity}`
    })
    .then(response => {
        if (response.ok) {
            updateCartTotal();
            showNotification('Cart updated', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating cart', 'error');
    });
}

function updateCartTotal() {
    const cartItems = document.querySelectorAll('.cart-item');
    let total = 0;
    
    cartItems.forEach(item => {
        const price = parseFloat(item.dataset.price);
        const quantity = parseInt(item.querySelector('.quantity-input').value);
        total += price * quantity;
    });
    
    const totalElement = document.querySelector('.cart-total');
    if (totalElement) {
        totalElement.textContent = `Rs. ${total.toFixed(2)}`;
    }
}

// Wishlist functionality
function toggleWishlist(productId) {
    const button = document.querySelector(`[data-product-id="${productId}"]`);
    if (!button) return;

    const isInWishlist = button.classList.contains('active');
    const url = isInWishlist ? `/wishlist/remove/${productId}/` : `/wishlist/add/${productId}/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (isInWishlist) {
            button.classList.remove('active');
            button.innerHTML = '<i class="far fa-heart"></i>';
            showNotification('Removed from wishlist', 'success');
        } else {
            button.classList.add('active');
            button.innerHTML = '<i class="fas fa-heart"></i>';
            showNotification('Added to wishlist', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating wishlist', 'error');
    });
}

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    if (!searchInput) return;

    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length >= 2) {
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 500);
        }
    });
}

function performSearch(query) {
    // Show loading state
    const searchResults = document.querySelector('.search-results');
    if (searchResults) {
        searchResults.innerHTML = '<div class="text-center"><div class="spinner"></div> Searching...</div>';
    }

    fetch(`/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.text())
        .then(html => {
            if (searchResults) {
                searchResults.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Search error:', error);
            if (searchResults) {
                searchResults.innerHTML = '<div class="text-center text-danger">Error performing search</div>';
            }
        });
}

// Product image gallery
function initializeProductGallery() {
    const productImages = document.querySelectorAll('.product-image-thumbnail');
    const mainImage = document.querySelector('.product-main-image');
    
    if (!productImages.length || !mainImage) return;
    
    productImages.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            const newSrc = this.dataset.fullImage;
            if (newSrc) {
                mainImage.src = newSrc;
                
                // Update active thumbnail
                productImages.forEach(img => img.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
}

// Quantity selector
function initializeQuantitySelectors() {
    document.querySelectorAll('.quantity-selector').forEach(selector => {
        const minusBtn = selector.querySelector('.quantity-minus');
        const plusBtn = selector.querySelector('.quantity-plus');
        const input = selector.querySelector('.quantity-input');
        
        if (minusBtn && plusBtn && input) {
            minusBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value);
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
            
            plusBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value);
                input.value = currentValue + 1;
                input.dispatchEvent(new Event('change'));
            });
        }
    });
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Lazy loading for images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy');
        });
    }
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Mobile menu toggle
function initializeMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navbarToggler.contains(event.target) && !navbarCollapse.contains(event.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeSearch();
    initializeProductGallery();
    initializeQuantitySelectors();
    initializeSmoothScrolling();
    initializeLazyLoading();
    initializeFormValidation();
    initializeMobileMenu();
    
    // Add event listeners for wishlist buttons only (cart uses HTML forms now)
    document.addEventListener('click', function(event) {
        if (event.target.closest('.wishlist-btn')) {
            const button = event.target.closest('.wishlist-btn');
            const productId = button.dataset.productId;
            toggleWishlist(productId);
        }
    });
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize popovers
    if (typeof bootstrap !== 'undefined') {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    console.log('Everest Beauty platform initialized successfully!');
});

// Export functions for use in other scripts
window.EverestBeauty = {
    addToCart,
    removeFromCart,
    updateCartItemQuantity,
    toggleWishlist,
    showNotification,
    updateCartCount,
    updateWishlistCount
};
