const fileInput = document.getElementById('formFileMultiple');
const fileNameInput = document.getElementById('fileNameInput');
const selectFilesButton = document.getElementById('selectFilesButton');
const fileCountMessage = document.getElementById('fileCountMessage');
const maxFiles = 10;

// When the file selection button is clicked, open the file selection window
selectFilesButton.addEventListener('click', () => {
  fileInput.click();
});

// After selecting the file, display the file name
fileInput.addEventListener('change', () => {
  let fileNames = Array.from(fileInput.files).map(file => file.name);

  // Process the file count limit
  if (fileNames.length > maxFiles) {
    alert(`최대 ${maxFiles}개의 파일만 선택할 수 있습니다.`);
    const dataTransfer = new DataTransfer();
    Array.from(fileInput.files)
      .slice(0, maxFiles)
      .forEach(file => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;
    fileNames = Array.from(fileInput.files).map(file => file.name);
  }

  // Update the file name
  fileNameInput.value = fileNames.join(', ') || '선택된 파일 없음';

  // Update the file count message
  fileCountMessage.textContent = `선택된 파일: ${fileInput.files.length}개 / 최대 ${maxFiles}개`;
});