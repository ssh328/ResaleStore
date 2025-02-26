function updateLikeCounter (post_id, heartIcon) {
    fetch(`/increase/${post_id}`, { method: 'POST' })
        .then(response => response.json())
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