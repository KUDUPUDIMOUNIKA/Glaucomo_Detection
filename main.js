
document.addEventListener('DOMContentLoaded', function() {
    // Contact form validation
    const contactForm = document.querySelector('form[action="/contact"]');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const message = document.getElementById('message').value.trim();
            
            if (!name || !email || !message) {
                e.preventDefault();
                alert('Please fill in all fields');
            }
        });
    }
    
    // Image upload preview (for predict page)
    const imageUpload = document.getElementById('eye_image');
    if (imageUpload) {
        imageUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const preview = document.getElementById('image-preview');
                if (preview) {
                    preview.src = URL.createObjectURL(file);
                    preview.style.display = 'block';
                }
            }
        });
    }
    
    // Auto-dismiss flash messages
    const flashes = document.querySelectorAll('.alert');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        }, 5000);
    });
});