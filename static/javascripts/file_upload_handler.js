const fileInput = document.getElementById('formFileMultiple');
const fileNameInput = document.getElementById('fileNameInput');
const selectFilesButton = document.getElementById('selectFilesButton');
const fileCountMessage = document.getElementById('fileCountMessage');
const maxFiles = 10;

// 파일 선택 버튼이 클릭되면 파일 선택 창을 실행
selectFilesButton.addEventListener('click', () => {
  fileInput.click();
});

// 파일을 선택한 후 파일 이름을 표시
fileInput.addEventListener('change', () => {
  let fileNames = Array.from(fileInput.files).map(file => file.name);

  // 파일 수 제한 처리
  if (fileNames.length > maxFiles) {
    alert(`최대 ${maxFiles}개의 파일만 선택할 수 있습니다.`);
    const dataTransfer = new DataTransfer();
    Array.from(fileInput.files)
      .slice(0, maxFiles)
      .forEach(file => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;
    fileNames = Array.from(fileInput.files).map(file => file.name);
  }

  // 파일 이름 업데이트
  fileNameInput.value = fileNames.join(', ') || '선택된 파일 없음';

  // 파일 수 메시지 업데이트
  fileCountMessage.textContent = `선택된 파일: ${fileInput.files.length}개 / 최대 ${maxFiles}개`;
});