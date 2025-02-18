// redirect_url이 존재할 경우 해당 URL로 리디렉션
const chatContainer = document.getElementById('chat-container');
const redirectUrl = chatContainer.dataset.redirectUrl;

if (redirectUrl) {
    // redirectUrl에서 roomid, receive_user_id, receive_user_name 추출
    const url = redirectUrl;
    console.log(url);
    const roomId = url.match(/new_chat_room_id=([^&]*)/)[1];
    console.log(roomId);
    const receiveUserId = url.match(/\/chat\/get_messages\/([^?]*)/)[1];
    console.log(receiveUserId);
    const receiveUserName = url.match(/receive_user_name=([^&]*)/)[1];
    console.log(receiveUserName);

    // 채팅 UI 요소들의 표시 상태 설정
    document.getElementById('chat-room-widget-content').style.display = 'block';

    // chat-content 표시
    document.querySelector('.chat-content').style.display = 'block';

    document.getElementById('chat-room-title').style.display = 'block'; // 제목 컨테이너 표시
    document.getElementById('chat-room-title').textContent = receiveUserName; // 상대방 이름 설정

    // 첫 번째 AJAX 요청: 채팅방 입장 처리
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
            // 성공 시 채팅방으로 이동
            console.log(`성공 ${data.room_id}, ${data.receive_user_name}`);

            // 전역 변수에 값 할당
            CURRENT_USER = data.current_user.name;
            ROOM_ID = data.room_id;
            RECEIVE_USER_NAME = data.receive_user_name;

            // 기존 메시지 목록 초기화
            document.getElementById('messages').innerHTML = '';

            // 날짜 구분선을 위한 변수 초기화
            lastDate = null;

            // 소켓 연결 및 채팅방 입장
            socket.emit("join", {
                "current_user": CURRENT_USER,
                "room_id": ROOM_ID
            });

            // 이전 메시지 표시
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
            // 실패 시 에러 메시지 표시
            alert('채팅방 입장에 실패했습니다.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('오류가 발생했습니다.');
    });

}


let socket = io();
let CURRENT_USER = null;
let ROOM_ID = null;
let RECEIVE_USER_NAME = null;

// 모든 채팅방 아이템에 대해 클릭 이벤트 리스너 추가
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
        
        // 이전 채팅방이 있고, 새로운 방이 다른 경우에만 stay_join 실행
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
            .then(response => response.json())  // 응답을 JSON으로 파싱
            .catch(error => {
                console.error('Error:', error);
            });
        }
        // 채팅 UI 요소들의 표시 상태 설정
        document.getElementById('chat-room-widget-content').style.display = 'block';
        document.querySelector('.chat-content').style.display = 'block';
        
        // 클릭된 채팅방의 데이터 속성 값들을 가져옴
        const roomId = this.getAttribute('data-room-id');
        const receiveUserId = this.getAttribute('data-receive-user-id');
        const receiveUserName = this.getAttribute('data-receive-user-name');

        document.getElementById('chat-room-title').style.display = 'block'; // 제목 컨테이너 표시
        document.getElementById('chat-room-title').textContent = receiveUserName; // 상대방 이름 설정
        // document.getElementById('leave_chat_btn').style.display = 'block'; // 채팅방 나가기 버튼 표시

        // 첫 번째 AJAX 요청: 채팅방 입장 처리
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
                // 성공 시 채팅방으로 이동
                console.log(`성공 ${data.room_id}, ${data.receive_user_name}`);

                // 전역 변수에 값 할당
                CURRENT_USER = data.current_user.name;
                ROOM_ID = data.room_id;
                RECEIVE_USER_NAME = data.receive_user_name;

                // 기존 메시지 목록 초기화
                document.getElementById('messages').innerHTML = '';

                // 날짜 구분선을 위한 변수 초기화
                lastDate = null;

                // 소켓 연결 및 채팅방 입장
                socket.emit("join", {
                    "current_user": CURRENT_USER,
                    "room_id": ROOM_ID
                });

                // 이전 메시지 표시
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
                // 실패 시 에러 메시지 표시
                alert('채팅방 입장에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('오류가 발생했습니다.');
        });
    });
});


// 상태 메시지 처리 (입장/퇴장 등)
socket.on('status', function (d) {
    const messages = document.getElementById('messages');
    const li = document.createElement('li');
    const statusDiv = document.createElement('div');

    statusDiv.classList.add('status-divider');
    statusDiv.textContent = d.data;

    li.appendChild(statusDiv);
    messages.appendChild(li);

    // 스크롤을 최하단으로 이동
    const msgsContainer = document.getElementById('msgs-container');
    msgsContainer.scrollTop = msgsContainer.scrollHeight;
});

// 메시지 입력 처리
const input = document.getElementById('text');
// let currentRoomInfo = { CURRENT_USER: null, ROOM_ID: null, receive_user_name: null };
input.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        const message = input.value;
        input.value = ''
        // 메시지 전송
        socket.emit('message', {
            'message': message,
            'current_user': CURRENT_USER,
            'room_id': ROOM_ID,
            'receive_user_name': RECEIVE_USER_NAME
        });
    }
});

// 날짜 구분선을 위한 변수
let lastDate = null;

// 날짜 구분선 생성 함수
function createDateDivider(messageDate) {
    // messages 요소 참조
    const messages = document.getElementById('messages');

    // 새로운 li와 div 요소 생성
    const li = document.createElement('li');
    const dateDiv = document.createElement('div');

    // date-divider 클래스 추가하여 스타일 적용
    dateDiv.classList.add('date-divider');

    // 날짜 형식 설정
    const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };

    // 날짜 한국어 형식으로 변환
    dateDiv.textContent = messageDate.toLocaleDateString('ko-KR', options);

    // li 요소에 dateDiv 추가
    li.appendChild(dateDiv);

    // messages 요소에 li 추가
    messages.appendChild(li);
}

// 채팅 메시지 아이템 생성 함수
function createChatItem(sender_name, text, receive_user_name, timestamp = null, room_id) {
    // timestamp가 있으면 timestamp를 사용하고, 없으면 현재 시간을 사용
    const messageDate = timestamp ? new Date(timestamp) : new Date();

    // 날짜가 변경되었거나 첫 메시지인 경우 날짜 구분선 추가
    const currentDate = messageDate.toDateString();
    if (lastDate !== currentDate) {
        createDateDivider(messageDate);
        lastDate = currentDate;
    }

    // DOM 요소 생성
    const messages = document.getElementById('messages');
    const li = document.createElement('li');
    const messageContainer = document.createElement('div');
    const nameSpan = document.createElement('span');
    const textSpan = document.createElement('span')
    const timeSpan = document.createElement('span'); // 시간 표시를 위한 새로운 span
    const msgsContainer = document.getElementById('msgs-container');

    // 현재 시간 가져오기
    const now = new Date();
    const hours = messageDate.getHours();
    const minutes = messageDate.getMinutes();
    const ampm = hours >= 12 ? '오후' : '오전';
    const formattedHours = hours % 12 || 12;
    const formattedTime = `${ampm} ${formattedHours}:${minutes.toString().padStart(2, '0')}`;

    // 이전 메시지의 시간과 발신자를 확인하기 위해 마지막 메시지 요소 가져오기
    const lastMessage = messages.lastElementChild;
    let showTime = true;

    if (lastMessage) {
        const lastMessageContainer = lastMessage.querySelector('div');
        const lastMessageTime = lastMessage.querySelector('.message-time');
        const isSameSender = (sender_name === CURRENT_USER && lastMessageContainer.classList.contains('my-message-container')) ||
                            (sender_name !== CURRENT_USER && lastMessageContainer.classList.contains('other-message-container'));
        
        // 이전 메시지의 시간과 현재 메시지의 시간이 같고 같은 발신자인 경우
        if (isSameSender && lastMessageTime && lastMessageTime.textContent === formattedTime) {
            // 이전 메시지의 시간을 숨김
            lastMessageTime.style.display = 'none';
            showTime = true; // 현재 메시지(마지막 메시지)에만 시간 표시
        }
    }

    // 시간 스타일 클래스 추가
    timeSpan.classList.add('message-time');
    if (showTime) {
        timeSpan.textContent = formattedTime;
    }

    // 현재 스크롤이 거의 맨 아래인지 확인 (여유값 10px)
    const isScrolledToBottom = msgsContainer.scrollHeight - msgsContainer.clientHeight - msgsContainer.scrollTop <= 10;

    // 메시지 스타일 클래스 추가
    nameSpan.classList.add('sender-name');
    textSpan.classList.add('message-text');

    // 메시지 타입에 따른 스타일 적용 (내 메시지/상대방 메시지)
    if (sender_name === CURRENT_USER) {
        // 내가 보낸 메시지인 경우
        messageContainer.classList.add('my-message-container');
        textSpan.textContent = text;
        messageContainer.appendChild(textSpan);
        messageContainer.appendChild(timeSpan); // 내 메시지의 경우 시간을 오른쪽에 표시
        // 내가 보낸 메시지는 항상 자동 스크롤로 최신 메시지 표시
        setTimeout(() => {
            msgsContainer.scrollTop = msgsContainer.scrollHeight;
        }, 0);
    } else {
        // 상대방이 보낸 메시지인 경우
        messageContainer.classList.add('other-message-container');
        textSpan.textContent = text;
        nameSpan.textContent = sender_name;
        messageContainer.appendChild(nameSpan);
        messageContainer.appendChild(textSpan);
        messageContainer.appendChild(timeSpan); // 상대방 메시지의 경우에도 시간 표시 
        // 사용자가 스크롤을 맨 아래에 위치시켰을 때만 자동 스크롤 실행
        if (isScrolledToBottom) {
            setTimeout(() => {
                msgsContainer.scrollTop = msgsContainer.scrollHeight;
            }, 0);
        }
    }

    // DOM에 요소 추가
    messageContainer.appendChild(nameSpan);
    messageContainer.appendChild(textSpan);
    messageContainer.appendChild(timeSpan);
    li.appendChild(messageContainer);
    messages.appendChild(li);
}

// 서버에서 받은 메시지 처리
socket.on('message', function (dt) {
    createChatItem(dt.sender_name, dt.text, dt.receive_user_name, dt.timestamp, dt.room_id);

    // 채팅 목록 업데이트
    const chatRoomItem = document.querySelector(`.chat-room-item[data-room-id="${dt.room_id}"]`);
    if (chatRoomItem) {
        // 최신 메시지 텍스트 업데이트
        const latestMessageElement = chatRoomItem.querySelector('.text-muted.text-truncate');
        if (latestMessageElement) {
            latestMessageElement.textContent = dt.text;
        }
        
        // 시간 업데이트
        const timeElement = chatRoomItem.querySelector('.text-muted');
        if (timeElement) {
            const messageDate = new Date(dt.timestamp);
            // UTC를 한국 시간(KST)으로 변환
            const kstDate = new Date(messageDate.getTime() + (9 * 60 * 60 * 1000));
            const formattedDate = kstDate.toISOString().split('T')[0];  // YYYY-MM-DD 형식
            timeElement.textContent = formattedDate;
        }

        // 채팅방 목록의 맨 위로 이동
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

// // 서버로부터의 응답을 처리하는 리스너 추가
socket.on('leave_response', (response) => {
    if (response.success) {
        console.log('채팅방 나가기 성공');
        window.location.href = '/chat/chat_room';
    } else {
        alert(response.message || '채팅방을 나가는데 실패했습니다.');
    }
});


// 페이지 이동 시 stay_join False로 변경
window.addEventListener('beforeunload', function(e) {
    if (CURRENT_USER && ROOM_ID) {
        // 새로고침 여부 확인
        if (e.currentTarget.performance.navigation.type !== 1) {  // 1은 새로고침을 의미
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
    }
});