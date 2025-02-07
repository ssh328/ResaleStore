from flask import render_template, url_for, request, redirect, Blueprint, make_response, jsonify
from flask_login import current_user
from datetime import datetime
from flask_socketio import SocketIO, join_room, leave_room, emit
from sqlalchemy import or_, and_

from model.data import Room, Message, db, User
from securityyy.security import admin_only

from app import app

chatting = Blueprint('chatting', __name__, template_folder='templates/chat')

socketio = SocketIO(app, cors_allowed_origins="*")

# 채팅방 페이지
@chatting.route('/chat_room', methods=['POST', 'GET'])
@admin_only
def chat_room():
    # # 캐시 제어를 위한 헤더 추가, 항상 최신 데이터를 표시하도록 보장함
    # # make_response(): 응답 객체를 생성하고 캐시 제어 헤더를 추가하는 함수
    # response = make_response(render_template('chat/new_chat_room.html', 
    #                                       chat_room_list=get_chat_rooms(),
    #                                       logged_in=current_user.is_authenticated))
    # # no-chche: 브라우저는 캐시된 데이터를 사용하기 전에 항상 서버에서 최신 데이터를 요청함
    # # no-store: 브라우저는 캐시된 데이터를 저장하지 않음
    # # must-revalidate: 캐시된 데이터가 유효하지 않은 경우, 반드시 서버에 데이터를 확인해야 함
    # response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    # # Pragma: no-cache 캐시를 비활성화 하기 위해 사용
    # response.headers['Pragma'] = 'no-cache'
    # # Expires: 0 캐시 만료 시간을 0으로 설정하여 캐시된 데이터가 만료되도록 함
    # response.headers['Expires'] = '0'
    # return response
    return render_template('chat/new_chat_room.html', 
                          chat_room_list=get_chat_rooms(),
                          logged_in=current_user.is_authenticated)

# 채팅방 목록 가져오기
def get_chat_rooms():
    user_id = current_user.id
    rooms = Room.query.filter(or_(Room.sender_id == user_id, Room.receiver_id == user_id)).all()
    chat_room_list = []    
    
    def get_other_user_info(room):
        # 현재 사용자가 아닌 상대방 정보 가져오기
        other_user_id = room.receiver_id if room.sender_id == user_id else room.sender_id
        other_user = User.query.get(other_user_id)

        # 상대방 정보가 없을 경우 처리
        if other_user is None:
            room_check = Room.query.get(room.id)
            # print(room_check)
        else:
            # 다른 사용자 정보가 있을 경우 room_check를 가져오는 로직 추가
            room_check = Room.query.filter(
                or_(
                    and_(Room.sender_id == current_user.id, Room.receiver_id == other_user.id),
                    and_(Room.sender_id == other_user.id, Room.receiver_id == current_user.id)
                )
            ).first()

        # 최신 메시지 가져오기
        latest_message = Message.query.filter_by(room_id=room_check.id).order_by(Message.time.desc()).first()

        message_time = latest_message.time.strftime('%Y-%m-%d')
        
        # 채팅방 상태 확인
        is_sender = user_id == room_check.sender_id
        room_status = room_check.sender_join if is_sender else room_check.receiver_join

        return {
            'email': other_user.email if other_user else 'Unknown',
            'receive_user_id': other_user.id if other_user else 'Unknown',
            'room_id': room_check.id,
            'room_check': room_status,
            'receiver_name': other_user.name if other_user else 'Unknown',
            'latest_message': latest_message.text,
            'message_time': message_time,
            'other_user_profile': other_user.profile_image_name if other_user else None,
        }

    for room in rooms:
        chat_room_list.append(get_other_user_info(room))
        
    return chat_room_list

# 채팅 페이지
@chatting.route('/get_messages/<string:receive_user_id>', methods=['GET', 'POST'])
@admin_only
def chat(receive_user_id):
    # receive_user_id: 메시지를 받게 되는 사람
    receive_user_id = receive_user_id

    if request.method == 'GET':
        receive_user_name = request.args.get('receive_user_name')
        room_id = request.args.get('room_id')

    if request.method == 'POST':
        data = request.get_json()
            
        # 데이터 추출
        room_id = data.get('room_id')
        receive_user_name = data.get('receive_user_name')

    # current_user: 채팅하기 눌렀을 때 메시지를 처음 보내는 사람
    room = Room.query.filter(
        or_(
            and_(Room.sender_id == current_user.id, Room.receiver_id == receive_user_id),
            and_(Room.sender_id == receive_user_id, Room.receiver_id == current_user.id)
        )
    ).first()

    if not room:
        new_chat_room = Room(
            sender_id=current_user.id,
            receiver_id=receive_user_id,
            sender_join=True,
            receiver_join=True
        )
        db.session.add(new_chat_room)
        db.session.commit()

        room = new_chat_room

    # room_id가 존재하면 해당 room_id로, 그렇지 않으면 room.id로 chat_room을 가져옴
    chat_room = db.get_or_404(Room, room_id if room_id else room.id)
    # print(chat_room)

    if current_user.id != chat_room.sender_id and current_user.id != chat_room.receiver_id:
        return redirect(url_for('index'))

    if current_user.id == chat_room.sender_id:
        if chat_room.sender_join == False:
            chat_room.sender_join = True
            chat_room.sender_last_join = datetime.now()
            db.session.commit()

        if chat_room.sender_last_join is None:
            messages = Message.query.filter_by(room_id=chat_room.id).order_by(Message.time).all()  # 시간순 정렬 추가
        else:
            messages = Message.query.filter_by(room_id=chat_room.id).filter(Message.time >= chat_room.sender_last_join).order_by(Message.time).all()
        
        return jsonify({
            'user': current_user.name,
            'room_id': chat_room.id,
            'receive_user_name': receive_user_name,
            'messages': [
                {
                    'id': message.id,
                    'room_id': message.room_id,
                    'sender_name': message.sender_name,
                    'receive_user_name': message.receive_user_name,
                    'text': message.text,
                    'time': message.time.isoformat()
                } for message in messages
            ],
            'logged_in': current_user.is_authenticated,
            'receive_user_id': receive_user_id
        })

    elif current_user.id == chat_room.receiver_id:
        if chat_room.receiver_join == False:
            chat_room.receiver_join = True
            chat_room.receiver_last_join = datetime.now()
            db.session.commit()

        if chat_room.receiver_last_join is None:
            messages = Message.query.filter_by(room_id=chat_room.id).all()  # 모든 메시지
        else:
            messages = Message.query.filter_by(room_id=chat_room.id).filter(Message.time >= chat_room.receiver_last_join).all()

        return jsonify({
            'user': current_user.name,
            'room_id': chat_room.id,
            'receive_user_name': receive_user_name,
            'messages': [
                {
                    'id': message.id,
                    'room_id': message.room_id,
                    'sender_name': message.sender_name,
                    'receive_user_name': message.receive_user_name,
                    'text': message.text,
                    'time': message.time.isoformat()
                } for message in messages
            ],
            'logged_in': current_user.is_authenticated,
            'receive_user_id': receive_user_id
        })

@socketio.on("connect")
def test_connect():
    print('connect!')


@socketio.on('join')
def join(data):
    room = data['room_id']
    name = data['current_user']
    join_room(room)


@socketio.on('message')
def handle_message(data):
    room = data['room_id']
    name = data['current_user']
    message = data['message']
    receive_user_name = data['receive_user_name']
    # print('received message: ' + message)
    # print(receive_user_name)
    current_time = datetime.now()

    # 메시지를 데이터베이스에 저장
    new_message = Message(
        room_id=room,
        sender_name=name,
        receive_user_name=receive_user_name,
        text=message,
        time=current_time
    )
    db.session.add(new_message)
    db.session.commit()

    # # 저장된 메시지의 타임스탬프 가져오기
    # saved_message = Message.query.get(new_message.id)

    # 저장된 타임스탬프를 사용하여 메시지 전송
    emit('message', {
        'sender_name': name, 
        'text': message, 
        'receive_user_name': receive_user_name,
        'timestamp': current_time.isoformat()  # 저장된 시간 사용
    }, to=room)
    # print(f"saved_message.time.isoformat(): {saved_message.time.isoformat()}")


@socketio.on('leave')
def on_leave(data):
    room = data['room_id']
    name = data['current_user']
    receive_user_id = data['receive_user_id']
    
    chat_room = Room.query.filter(
        or_(
            and_(Room.sender_id == current_user.id, Room.receiver_id == receive_user_id),
            and_(Room.sender_id == receive_user_id, Room.receiver_id == current_user.id)
        )
    ).first()
    
    if current_user.id == chat_room.sender_id:
        chat_room.sender_join = False
    else:
        chat_room.receiver_join = False
    
    # 두 사용자 모두 채팅방을 나갔을 경우
    if not chat_room.sender_join and not chat_room.receiver_join:
        # 해당 채팅방의 모든 메시지 삭제
        Message.query.filter_by(room_id=chat_room.id).delete()
        # 채팅방 삭제
        db.session.delete(chat_room)
    
    db.session.commit()
    
    leave_room(room)
    print(f"{name} {room}방, bye")
    emit('status', {'data': f"{name}님이 나갔습니다."}, to=room)


@socketio.on('disconnect')
def test_disconnect(reason):
    print('Client disconnected, reason:', reason)