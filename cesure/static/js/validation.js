// Form validation for Cesure forms

document.addEventListener('DOMContentLoaded', function() {
    // Registration form validation
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            const email = document.getElementById('email').value;
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const passwordConfirm = document.getElementById('password_confirm').value;
            let isValid = true;
            let errorMessage = '';
            
            // Clear previous error messages
            document.querySelectorAll('.error-message').forEach(el => el.remove());
            
            // Email validation
            if (!validateEmail(email)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
                showError('email', errorMessage);
            }
            
            // Username validation (3-50 characters)
            if (username.length < 3 || username.length > 50) {
                isValid = false;
                errorMessage = 'Username must be between 3 and 50 characters';
                showError('username', errorMessage);
            }
            
            // Password validation (min 8 characters)
            if (password.length < 8) {
                isValid = false;
                errorMessage = 'Password must be at least 8 characters';
                showError('password', errorMessage);
            }
            
            // Password confirmation
            if (password !== passwordConfirm) {
                isValid = false;
                errorMessage = 'Passwords do not match';
                showError('password_confirm', errorMessage);
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    // Login form validation
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            let isValid = true;
            
            // Clear previous error messages
            document.querySelectorAll('.error-message').forEach(el => el.remove());
            
            // Email validation
            if (!validateEmail(email)) {
                isValid = false;
                showError('email', 'Please enter a valid email address');
            }
            
            // Password validation
            if (password.length === 0) {
                isValid = false;
                showError('password', 'Password is required');
            }
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
});

// Helper functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.textContent = message;
    
    // Insert error message after the field
    field.parentNode.insertBefore(errorElement, field.nextSibling);
}