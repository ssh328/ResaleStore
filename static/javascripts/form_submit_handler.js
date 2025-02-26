// After validating the form, display the loading
document.querySelector('form').addEventListener('submit', function(event) {
    const saveButton = document.getElementById('saveButton');
    const originalWidth = saveButton.offsetWidth; // Save the original width
    
    if (!this.checkValidity()) {
        // Validate the form, return true if it is invalid
        event.preventDefault(); // Prevent submission if validation fails
        this.classList.add('was-validated'); // Add the validation style
        return;
    }
    
    saveButton.innerHTML = `
            <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
            <span class="visually-hidden" role="status">Loading...</span>
    `;
    saveButton.style.width = originalWidth + 'px'; // Set the original width
    saveButton.disabled = true; // Disable the button
});