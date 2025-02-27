// 부트스트랩 유효성 검사 코드
(() => {
    'use strict'
  
    // 유효성 검사 스타일을 적용할 모든 폼 가져오기
    const forms = document.querySelectorAll('.validated-form')
  
    // 반복하여 제출 방지
    Array.from(forms).forEach(form => {
       form.addEventListener('submit', event => {
       if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
       }
       form.classList.add('was-validated')
       }, false)
    })
  })()