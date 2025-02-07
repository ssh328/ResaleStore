from flask import render_template, url_for, request, redirect, Blueprint
from flask_login import current_user
from datetime import datetime
from flask_socketio import SocketIO, join_room, leave_room, emit
from sqlalchemy import or_, and_

from model.data import Room, Message, db
from securityyy.security import admin_only

from app import app

chatting = Blueprint('chatting', __name__, template_folder='templates/chat')

socketio = SocketIO(app, cors_allowed_origins="*")


# 채팅 페이지
@chatting.route('/<receive_user_id>', methods = ['GET'])
@admin_only
def chat(receive_user_id):
    # receive_user_id: 메시지를 받게 되는 사람
    receive_user_id = receive_user_id
    # print(f"Received user_id: {receive_user_id}")  # 디버깅을 위한 출력
    receive_user_name = request.args.get('receive_user_name')
    # print(f"Received user_name: {receive_user_name}")
    room_id = request.args.get('room_id')
    # print(f"Received room_id: {room_id}")


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

        return render_template('chat/chatting.html', user=current_user.name, room_id=chat_room.id,
                               receive_user_name=receive_user_name, messages=messages, logged_in=current_user.is_authenticated,
                               receive_user_id=receive_user_id)

    elif current_user.id == chat_room.receiver_id:
        if chat_room.receiver_join == False:
            chat_room.receiver_join = True
            chat_room.receiver_last_join = datetime.now()
            db.session.commit()

        if chat_room.receiver_last_join is None:
            messages = Message.query.filter_by(room_id=chat_room.id).all()  # 모든 메시지
        else:
            messages = Message.query.filter_by(room_id=chat_room.id).filter(Message.time >= chat_room.receiver_last_join).all()

        return render_template('chat/chatting.html', user=current_user.name, room_id=chat_room.id,
                               receive_user_name=receive_user_name, messages=messages, logged_in=current_user.is_authenticated,
                               receive_user_id=receive_user_id)


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