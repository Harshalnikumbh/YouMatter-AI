// YouMatter - Simplified JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }

    // Character counter for emotion input
    const emotionInput = document.querySelector('.emotion-input');
    const charCount = document.querySelector('.char-count');
    
    if (emotionInput && charCount) {
        emotionInput.addEventListener('input', function() {
            const count = this.value.length;
            charCount.textContent = `${count} characters`;
            
            // Visual feedback based on length
            if (count > 500) {
                charCount.style.color = '#FFCC80';
            } else if (count > 1000) {
                charCount.style.color = '#FF8A80';
            } else {
                charCount.style.color = '#8A8A8A';
            }
        });
    }

    // Form submission with loading state
    const emotionForm = document.querySelector('form[action*="submit_emotion"]');
    if (emotionForm) {
        emotionForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const btnText = submitBtn.querySelector('.btn-text');
            const spinner = submitBtn.querySelector('.spinner-border');
            
            if (submitBtn && btnText && spinner) {
                // Show loading state
                submitBtn.disabled = true;
                submitBtn.classList.add('btn-loading');
                btnText.style.opacity = '0';
                spinner.classList.remove('d-none');
                
                // Simulate processing time (remove in production)
                setTimeout(() => {
                    // Form will submit naturally after this
                }, 1000);
            }
        });
    }

    // Contact form handling
    const contactForm = document.querySelector('form[action*="contact_submit"]');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i data-feather="loader" width="16" height="16"></i> Sending...';
                feather.replace();
            }
        });
    }

    // Sign-in modal functionality
    window.showSigninModal = function() {
        const modal = new bootstrap.Modal(document.getElementById('signinModal'));
        modal.show();
    };

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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

    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation
    document.querySelectorAll('.needs-validation').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
});

// Utility functions
function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

function showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}
