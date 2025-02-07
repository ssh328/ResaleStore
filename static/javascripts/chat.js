let socket = io();
let current_user = '';
let room_id = '';

fetch('/chat/95537fd8-f966-45c3-9eef-8c686afae4c8')
    .then(response => response.json())
    .then(data => {
        current_user = data.current_user;
        room_id = data.room_id;
    });

socket.on('connect', function() {
    socket.emit('join', {
    'current_user': current_user,
    'room_id': room_id
    });
});

socket.on('status', function (data) {
    const messages = document.getElementById('messages');
    const li = document.createElement('li');
    li.textContent = data;
    messages.appendChild(li);
    messages.scrollTop = messages.scrollHeight;
});

const input = document.getElementById('text');
input.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        const message = input.value;
        input.value = ''
        socket.emit('message', {
        'message': message,
        'current_user': current_user,
        'room_id': room_id
        });
    }
});

socket.on('message', function (data) {
    const messages = document.getElementById('messages');
    const li = document.createElement('li');

    if (data.name === current_user) {
        li.textContent = `You: ${data.msg}`;
        li.classList.add('my-message');
    } else {
        li.textContent = `${data.name}: ${data.msg}`;
        li.classList.add('other-message');
    }

    messages.appendChild(li);
    messages.scrollTop = messages.scrollHeight;
});


const leave_btn = document.getElementById('leave_chat_btn');
leave_btn.addEventListener('click', () => {
    socket.emit('leave', {
    'current_user': current_user,
    'room_id': room_id
    })
});