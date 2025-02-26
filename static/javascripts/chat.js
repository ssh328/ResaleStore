let socket = io();
let CURRENT_USER = null;
let ROOM_ID = null;
let RECEIVE_USER_NAME = null;
// Redirect to the specified URL if redirect_url exists
const chatContainer = document.getElementById('chat-container');
const redirectUrl = chatContainer.dataset.redirectUrl;

if (redirectUrl) {
    // Extract roomid, receive_user_id, receive_user_name from redirectUrl
    const url = redirectUrl;
    const roomId = url.match(/new_chat_room_id=([^&]*)/)[1];
    const receiveUserId = url.match(/\/chat\/get_messages\/([^?]*)/)[1];
    const receiveUserName = url.match(/receive_user_name=([^&]*)/)[1];

    // Set the display status of the chat UI elements
    document.getElementById('chat-room-widget-content').style.display = 'block';
    // Display chat-content
    document.querySelector('.chat-content').style.display = 'block';
    document.getElementById('chat-room-title').style.display = 'block'; // Display the title container
    document.getElementById('chat-room-title').textContent = receiveUserName; // Set the name of the other user

    fetch('/chat/reset_unread_count', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            room_id: roomId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const unreadBadge = document.querySelector('.badge');
            if (unreadBadge) {
                unreadBadge.remove();
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });

    // Process the chat room entry
    fetch(redirectUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            room_id: roomId,
            receive_user_name: receiveUserName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data) {
            // When successful, move to the chat room

            // Assign values to global variables
            CURRENT_USER = data.current_user.name;
            ROOM_ID = data.room_id;
            RECEIVE_USER_NAME = data.receive_user_name;

            // Initialize the list of existing messages
            document.getElementById('messages').innerHTML = '';

            // Initialize the variable for the date divider
            lastDate = null;

            // Connect to the socket and enter the chat room
            socket.emit("join", {
                "current_user": CURRENT_USER,
                "room_id": ROOM_ID
            });

            // Display the previous messages
            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(message => {
                    createChatItem(
                        message.sender_name,
                        message.text,
                        message.receive_user_name,
                        message.time
                    );
                });
            }
        } else {
            // When failed, display the error message
            alert('채팅방 입장에 실패했습니다.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('오류가 발생했습니다.');
    });

}

// Add a click event listener to all chat room items
document.querySelectorAll('.chat-room-item').forEach(item => {
    item.addEventListener('click', function() {
        const newRoomId = this.getAttribute('data-room-id');

        fetch('/chat/reset_unread_count', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: newRoomId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const unreadBadge = this.querySelector('.badge');
                if (unreadBadge) {
                    unreadBadge.remove();
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
        
        // If there is a previous chat room and the new room is different, execute stay_join
        if (ROOM_ID && ROOM_ID !== newRoomId) {
            fetch('/chat/stay_join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    current_user: CURRENT_USER,
                    room_id: ROOM_ID
                })
            })
            .then(response => response.json())
            .catch(error => {
                console.error('Error:', error);
            });
        }
        // Get the data attributes of the clicked chat room
        const roomId = this.getAttribute('data-room-id');
        const receiveUserId = this.getAttribute('data-receive-user-id');
        const receiveUserName = this.getAttribute('data-receive-user-name');

        // Set the display status of the chat UI elements
        document.getElementById('chat-room-widget-content').style.display = 'block';
        document.querySelector('.chat-content').style.display = 'block';
        document.getElementById('chat-room-title').style.display = 'block'; // Display the title container
        document.getElementById('chat-room-title').textContent = receiveUserName; // Set the name of the other user

        // Process the chat room entry
        fetch(`/chat/get_messages/${receiveUserId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: roomId,
                receive_user_name: receiveUserName
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data) {
                // When successful, move to the chat room

                // Assign values to global variables
                CURRENT_USER = data.current_user.name;
                ROOM_ID = data.room_id;
                RECEIVE_USER_NAME = data.receive_user_name;

                // Initialize the list of existing messages
                document.getElementById('messages').innerHTML = '';

                // Initialize the variable for the date divider
                lastDate = null;

                // Connect to the socket and enter the chat room
                socket.emit("join", {
                    "current_user": CURRENT_USER,
                    "room_id": ROOM_ID
                });

                // Display the previous messages
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(message => {
                        createChatItem(
                            message.sender_name,
                            message.text,
                            message.receive_user_name,
                            message.time
                        );
                    });
                }
            } else {
                // When failed, display the error message
                alert('채팅방 입장에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('오류가 발생했습니다.');
        });
    });
});

// Process the status message (entering/leaving, etc.)
socket.on('status', function (d) {
    const messages = document.getElementById('messages');
    const li = document.createElement('li');
    const statusDiv = document.createElement('div');

    statusDiv.classList.add('status-divider');
    statusDiv.textContent = d.data;

    li.appendChild(statusDiv);
    messages.appendChild(li);

    // Move the scroll to the bottom
    const msgsContainer = document.getElementById('msgs-container');
    msgsContainer.scrollTop = msgsContainer.scrollHeight;
});

// Process the message input
const input = document.getElementById('text');

input.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        const message = input.value;
        input.value = ''
        // Send the message
        socket.emit('message', {
            'message': message,
            'current_user': CURRENT_USER,
            'room_id': ROOM_ID,
            'receive_user_name': RECEIVE_USER_NAME
        });
    }
});

// Initialize the variable for the date divider
let lastDate = null;

// Create the date divider function
function createDateDivider(messageDate) {
    // Reference the messages element
    const messages = document.getElementById('messages');

    // Create a new li and div element
    const li = document.createElement('li');
    const dateDiv = document.createElement('div');

    // Add the date-divider class to apply the style
    dateDiv.classList.add('date-divider');

    // Set the date format
    const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };

    // Convert the date to Korean format
    dateDiv.textContent = messageDate.toLocaleDateString('ko-KR', options);

    // Add the dateDiv to the li element
    li.appendChild(dateDiv);

    // Add the li element to the messages element
    messages.appendChild(li);
}

// Create the chat message item function
function createChatItem(sender_name, text, receive_user_name, timestamp = null, room_id) {
    // If timestamp exists, use timestamp, otherwise use the current time
    const messageDate = timestamp ? new Date(timestamp) : new Date();

    // If the date has changed or it is the first message, add the date divider
    const currentDate = messageDate.toDateString();
    if (lastDate !== currentDate) {
        createDateDivider(messageDate);
        lastDate = currentDate;
    }

    // Create the DOM elements
    const messages = document.getElementById('messages');
    const li = document.createElement('li');
    const messageContainer = document.createElement('div');
    const nameSpan = document.createElement('span');
    const textSpan = document.createElement('span')
    const timeSpan = document.createElement('span'); // For displaying the time
    const msgsContainer = document.getElementById('msgs-container');

    // Get the current time
    const now = new Date();
    const hours = messageDate.getHours();
    const minutes = messageDate.getMinutes();
    const ampm = hours >= 12 ? '오후' : '오전';
    const formattedHours = hours % 12 || 12;
    const formattedTime = `${ampm} ${formattedHours}:${minutes.toString().padStart(2, '0')}`;

    // Get the last message element to check the time and sender of the previous message
    const lastMessage = messages.lastElementChild;
    let showTime = true;

    if (lastMessage) {
        const lastMessageContainer = lastMessage.querySelector('div');
        const lastMessageTime = lastMessage.querySelector('.message-time');
        const isSameSender = (sender_name === CURRENT_USER && lastMessageContainer.classList.contains('my-message-container')) ||
                            (sender_name !== CURRENT_USER && lastMessageContainer.classList.contains('other-message-container'));
        
        // If the time of the previous message and the current message are the same and the same sender, hide the time of the previous message
        if (isSameSender && lastMessageTime && lastMessageTime.textContent === formattedTime) {
            // Hide the time of the previous message
            lastMessageTime.style.display = 'none';
            showTime = true; // Display the time of the current message (the last message)
        }
    }

    // Add the time style class
    timeSpan.classList.add('message-time');
    if (showTime) {
        timeSpan.textContent = formattedTime;
    }

    // Check if the current scroll is almost at the bottom (10px margin)
    const isScrolledToBottom = msgsContainer.scrollHeight - msgsContainer.clientHeight - msgsContainer.scrollTop <= 10;

    // Add the message style class
    nameSpan.classList.add('sender-name');
    textSpan.classList.add('message-text');

    // Apply the style according to the message type (my message/other message)
    if (sender_name === CURRENT_USER) {
        // If it is my message
        messageContainer.classList.add('my-message-container');
        textSpan.textContent = text;
        messageContainer.appendChild(textSpan);
        messageContainer.appendChild(timeSpan); // For my message, display the time on the right
        // My message is always displayed with automatic scrolling to the latest message
        setTimeout(() => {
            msgsContainer.scrollTop = msgsContainer.scrollHeight;
        }, 0);
    } else {
        // If it is the other person's message
        messageContainer.classList.add('other-message-container');
        textSpan.textContent = text;
        nameSpan.textContent = sender_name;
        messageContainer.appendChild(nameSpan);
        messageContainer.appendChild(textSpan);
        messageContainer.appendChild(timeSpan); // For the other person's message, also display the time
        // Execute automatic scrolling only when the user scrolls to the bottom
        if (isScrolledToBottom) {
            setTimeout(() => {
                msgsContainer.scrollTop = msgsContainer.scrollHeight;
            }, 0);
        }
    }

    // Add the elements to the DOM
    messageContainer.appendChild(nameSpan);
    messageContainer.appendChild(textSpan);
    messageContainer.appendChild(timeSpan);
    li.appendChild(messageContainer);
    messages.appendChild(li);
}

// Process the message received from the server
socket.on('message', function (dt) {
    createChatItem(dt.sender_name, dt.text, dt.receive_user_name, dt.timestamp, dt.room_id);

    // Update the chat list
    const chatRoomItem = document.querySelector(`.chat-room-item[data-room-id="${dt.room_id}"]`);
    if (chatRoomItem) {
        // Update the latest message text
        const latestMessageElement = chatRoomItem.querySelector('.text-muted.text-truncate');
        if (latestMessageElement) {
            latestMessageElement.textContent = dt.text;
        }
        
        // Update the time
        const timeElement = chatRoomItem.querySelector('.text-muted');
        if (timeElement) {
            const messageDate = new Date(dt.timestamp);
            // Convert UTC to Korean time (KST)
            const kstDate = new Date(messageDate.getTime() + (9 * 60 * 60 * 1000));
            const formattedDate = kstDate.toISOString().split('T')[0];  // YYYY-MM-DD format
            timeElement.textContent = formattedDate;
        }

        // Move the chat room list to the top
        const chatRoomList = document.querySelector('.chat-room-list');
        chatRoomList.insertBefore(chatRoomItem, chatRoomList.firstChild);
    }
});

const leave_btn = document.getElementById('leave_chat_btn');
leave_btn.addEventListener('click', async () => {
    socket.emit('leave', {
        'current_user': CURRENT_USER,
        'room_id': ROOM_ID,
        'receive_user_name': RECEIVE_USER_NAME
    });
});

// Process the response from the server
socket.on('leave_response', (response) => {
    if (response.success) {
        console.log('채팅방 나가기 성공');
        window.location.href = '/chat/chat_room';
    } else {
        alert(response.message || '채팅방을 나가는데 실패했습니다.');
    }
});

// Process the response from the server
socket.on('leave_response', (response) => {
    if (response.success) {
        console.log('채팅방 나가기 성공');
        // Page redirection
        window.location.href = '/chat/chat_room';
    } else {
        alert(response.message || '채팅방을 나가는데 실패했습니다.');
    }
});


// When the page is moved, change stay_join to False
window.addEventListener('beforeunload', function(e) {
if (CURRENT_USER && ROOM_ID) {
    fetch('/chat/stay_join', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            current_user: CURRENT_USER,
            room_id: ROOM_ID
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('stay_join 실행');
        } else {
            console.error('stay_join 실행 실패');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
});