// 유효성 검사 후 로딩 중 표시
document.getElementById('deleteForm').addEventListener('submit', function(event) {
    const deleteButton = document.getElementById('deleteButton');
    const originalWidth = deleteButton.offsetWidth; // 원래 너비 저장

    // 폼의 유효성을 검사
    if (!this.checkValidity()) {
        event.preventDefault(); // 유효성 검사 실패 시 제출 방지
        this.classList.add('was-validated'); // 유효성 검사 스타일 추가
        return;
    }

    deleteButton.innerHTML = `
        <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
        <span class="visually-hidden" role="status">Loading...</span>
    `;
    deleteButton.style.width = originalWidth + 'px'; // 원래 너비로 설정
    deleteButton.disabled = true; // 버튼 비활성화
});