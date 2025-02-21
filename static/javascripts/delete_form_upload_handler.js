document.addEventListener('DOMContentLoaded', function() {
    const deleteModal = document.getElementById('deleteModal');
    
    if (deleteModal) {
        deleteModal.addEventListener('shown.bs.modal', function() {
            const deleteForm = document.getElementById('deleteForm');
            if (deleteForm) {
                deleteForm.addEventListener('submit', function(event) {
                    const deleteButton = document.getElementById('deleteButton');
                    const originalWidth = deleteButton.offsetWidth;

                    if (!this.checkValidity()) {
                        event.preventDefault();
                        this.classList.add('was-validated');
                        return;
                    }

                    deleteButton.innerHTML = `
                        <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
                        <span class="visually-hidden" role="status">Loading...</span>
                    `;
                    deleteButton.style.width = originalWidth + 'px';
                    deleteButton.disabled = true;
                });
            }
        });
    }
});