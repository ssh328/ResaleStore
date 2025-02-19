const deleteModal = document.getElementById('deleteModal')
const deleteInput = document.getElementById('deleteInput')

deleteModal.addEventListener('shown.bs.modal', () => {
  if (deleteInput) {
    deleteInput.focus()
  }
})

deleteModal.addEventListener('show.bs.modal', () => {
  deleteModal.removeAttribute('inert')
})

deleteModal.addEventListener('hide.bs.modal', () => {
  deleteModal.setAttribute('inert', '')
})