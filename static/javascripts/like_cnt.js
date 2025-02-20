// HTML <form>을 제출하고 리디렉션을 수행하여 템플릿을 다시 렌더링하는 대신 fetch()를 호출하고 페이지의 콘텐츠를 바꾸는 JavaScript를 추가
function updateLikeCounter (post_id, heartIcon) {
    fetch(`/increase/${post_id}`, { method: 'POST' })   // fetch() 는 URL과 다른 옵션이 포함된 객체라는 두 개의 인수를 취함
                                                        // 지정된 url 로 HTTP 요청을 보냄
        .then(response => response.json())
        // fetch 요청이 완료 되면 Promise 객체를 반환, 이 Promise 객체는 서버로 부터 받은 response 을 포함
        // .json() 메서드가 응답 본문을 JSON 형식으로 파싱, Promise 객체를 반환
        // response.json() 이 완료되면, JSON 데이터가 then 블록 내의 data 변수에 전달
        .then(data => {
            if (heartIcon.classList.contains('fa-solid')) {
                heartIcon.classList.remove('fa-solid', 'fa-bounce');
                heartIcon.classList.add('fa-regular');
                heartIcon.style.color = '#000000';
                heartIcon.style.removeProperty('--fa-animation-iteration-count');
            } else {
                heartIcon.classList.remove('fa-regular');
                heartIcon.classList.add('fa-solid', 'fa-bounce');
                heartIcon.style.color = '#ff0000';
                heartIcon.style.setProperty('--fa-animation-iteration-count', '1');
            }

            document.getElementById(`like-count-${post_id}`).textContent = data.like_cnt
        })
        .catch(e => console.error('Error:', e))
}

document.querySelectorAll('.increase-cnt-btn').forEach(heart_btn => {
    heart_btn.addEventListener('click', function() {
    const post_id = this.getAttribute('data-post-id');
    const heartIcon = this.querySelector('i');
    updateLikeCounter(post_id, heartIcon);
    })
})