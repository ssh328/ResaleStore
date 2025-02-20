document.getElementById('profile_edit_btn').addEventListener('click', () => {
    document.getElementById('file_input').click();
});

function toggleSubmitButton() {
    const fileInput = document.getElementById('file_input');
    const submitButton = document.getElementById('saveButton');
    const previewImg = document.getElementById('preview_img');
    const originalSrc = previewImg.dataset.originalSrc;    // 원본 이미지 경로
    
    submitButton.disabled = !fileInput.files.length
    submitButton.className = fileInput.files.length ? 'btn btn-warning ms-2' : 'btn btn-outline-warning ms-2'

    // 미리보기 이미지 업데이트
    if (fileInput.files.length) {
        const file = fileInput.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            document.getElementById('image_preview').style.display = 'block';
        }
        reader.readAsDataURL(file);
    } else {
        previewImg.src = originalSrc; // current_user.profile_image_name으로 복원
        document.getElementById('image_preview').style.display = 'block';   // 사진을 보이게 함
    }   
}