from flask import render_template, url_for, request, redirect, Blueprint, make_response, jsonify, flash
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
    if request.method == 'POST':
        receive_user_id = request.form.get('receive_user_id')
        receive_user_name = request.form.get('receive_user_name')
        current_time = datetime.now()

        # 기존 채팅방 확인
        room = Room.query.filter(
            or_(
                and_(Room.sender_id == current_user.id, Room.receiver_id == receive_user_id),
                and_(Room.sender_id == receive_user_id, Room.receiver_id == current_user.id)
            )
        ).first()

        if room:
            # 기존 방이 있고 현재 사용자가 sender인 경우
            if current_user.id == room.sender_id and not room.sender_join:
                room.sender_join = True
                room.sender_last_join = current_time
                db.session.commit()
            # 기존 방이 있고 현재 사용자가 receiver인 경우
            elif current_user.id == room.receiver_id and not room.receiver_join:
                room.receiver_join = True
                room.receiver_last_join = current_time
                db.session.commit()
        else:
            # 새 채팅방 생성
            room = Room(
                sender_id=current_user.id,
                receiver_id=receive_user_id,
                sender_join=True,
                receiver_join=True,
                date=current_time
            )
            db.session.add(room)
            db.session.commit()

        # # make_response(): 응답 객체를 생성하고 캐시 제어 헤더를 추가하는 함수
        response = make_response(render_template('chat/new_chat_room.html', 
                            chat_room_list=get_chat_rooms(),
                            logged_in=current_user.is_authenticated,
                            redirect_url=url_for('chatting.chat', 
                                               receive_user_id=receive_user_id, 
                                               new_chat_room_id=room.id, 
                                               receive_user_name=receive_user_name)))
    else:
        response = make_response(render_template('chat/new_chat_room.html', 
                            chat_room_list=get_chat_rooms(),
                            logged_in=current_user.is_authenticated))
    
    # # 캐시 제어를 위한 헤더 추가, 항상 최신 데이터를 표시하도록 보장함
    # # no-chche: 브라우저는 캐시된 데이터를 사용하기 전에 항상 서버에서 최신 데이터를 요청함
    # # no-store: 브라우저는 캐시된 데이터를 저장하지 않음
    # # must-revalidate: 캐시된 데이터가 유효하지 않은 경우, 반드시 서버에 데이터를 확인해야 함
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    # # Pragma: no-cache 캐시를 비활성화 하기 위해 사용
    response.headers['Pragma'] = 'no-cache'
    # # Expires: 0 캐시 만료 시간을 0으로 설정하여 캐시된 데이터가 만료되도록 함
    response.headers['Expires'] = '0'
    return response


# 채팅방 목록 가져오기
def get_chat_rooms():
    user_id = current_user.id
    rooms = Room.query.filter(or_(Room.sender_id == user_id, Room.receiver_id == user_id)).all()
    chat_room_list = []
    
    def get_other_user_info(room):
        # 현재 사용자가 아닌 상대방 정보 가져오기
        other_user_id = room.receiver_id if room.sender_id == user_id else room.sender_id
        other_user = User.query.get(other_user_id)
        room_check = Room.query.get(room.id)

        # 현재 사용자가 채팅방의 송신자인지 수신자인지 확인
        is_sender = user_id == room_check.sender_id
        is_receiver = user_id == room_check.receiver_id

        # 읽지 않은 메시지 수 가져오기
        if is_sender:
            unread_count = room_check.sender_unread_count
        elif is_receiver:
            unread_count = room_check.receiver_unread_count
        else:
            unread_count = 0

        # 최신 메시지 가져오기
        latest_message = Message.query.filter_by(room_id=room_check.id).order_by(Message.time.desc()).first()
        message_time = latest_message.time.strftime('%Y-%m-%d') if latest_message else room_check.date.strftime('%Y-%m-%d')
        
        # 채팅방 상태 확인
        if is_sender:
            last_join_time = room_check.sender_last_join
            if last_join_time is not None:
                latest_message = Message.query.filter_by(room_id=room_check.id).filter(
                    Message.time >= last_join_time
                ).order_by(Message.time.desc()).first()
            else:
                latest_message = Message.query.filter_by(room_id=room_check.id).order_by(Message.time.desc()).first()
        else:
            last_join_time = room_check.receiver_last_join
            if last_join_time is not None:
                latest_message = Message.query.filter_by(room_id=room_check.id).filter(
                    Message.time >= last_join_time
                ).order_by(Message.time.desc()).first()
            else:
                latest_message = Message.query.filter_by(room_id=room_check.id).order_by(Message.time.desc()).first()
        
        # 채팅방 상태 확인
        room_status = room_check.sender_join if is_sender else room_check.receiver_join

        return {
            'email': other_user.email if other_user else 'Unknown',
            'receive_user_id': other_user.id if other_user else 'Unknown',
            'room_id': room_check.id,
            'room_check': room_status,
            'receiver_name': other_user.name if other_user else 'Unknown',
            'latest_message': latest_message.text if latest_message else '대화가 없습니다.',
            'message_time': message_time,
            'other_user_profile': other_user.profile_image_name if other_user else None,
            'unread_count': unread_count
        }

    for room in rooms:
        chat_room_list.append(get_other_user_info(room))
        
    return chat_room_list


# 채팅 메시지 가져오기
@chatting.route('/get_messages/<string:receive_user_id>', methods=['GET', 'POST'])
@admin_only
def chat(receive_user_id):
    # receive_user_id: 메시지를 받게 되는 사람
    receive_user = User.query.get(receive_user_id)
    receive_user_name = receive_user.name if receive_user else None
    current_time = datetime.now()
    room_id = None

    if request.method == 'POST':
        data = request.get_json()
        room_id = data.get('room_id')

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
            receiver_join=True,
            date=current_time
        )
        db.session.add(new_chat_room)
        db.session.commit()

        room = new_chat_room

    # room_id가 존재하면 해당 room_id로, 그렇지 않으면 room.id로 chat_room을 가져옴
    chat_room = db.get_or_404(Room, room_id if room_id else room.id)

    if current_user.id != chat_room.sender_id and current_user.id != chat_room.receiver_id:
        return redirect(url_for('index'))

    if current_user.id == chat_room.sender_id:
        if chat_room.sender_join == False:
            chat_room.sender_join = True
            chat_room.sender_last_join = datetime.now()
            db.session.commit()

        # 채팅방 송신자의 마지막 접속 시간이 없는 경우 모든 메시지를 가져옴
        if chat_room.sender_last_join is None:
            messages = Message.query.filter_by(room_id=chat_room.id).order_by(Message.time).all()  # 시간순 정렬
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
            'receive_user_id': receive_user_id,
            'current_user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email
            }  # current_user 객체를 직접 전달하지 않고 필요한 속성만 딕셔너리로 전달
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
            'receive_user_id': receive_user_id,
            'current_user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email
            }  # current_user 객체를 직접 전달하지 않고 필요한 속성만 딕셔너리로 전달
        })


# stay_join: 사용자가 채팅방에 접속 중인지 확인
@chatting.route('/stay_join', methods=['POST'])
@admin_only
def update_stay_join():
    try:
        data = request.get_json()
        room = data.get('room_id')
        current_user = data.get('current_user')
        
        # 채팅방과 사용자가 존재하는지 확인
        chat_room = Room.query.get(room)
        if not chat_room:
            flash('채팅방을 찾을 수 없습니다.', 'danger')
            return redirect(url_for('chatting.chat_room'))
            
        user = User.query.filter_by(name=current_user).first()
        if not user:
            flash('사용자를 찾을 수 없습니다.', 'danger')
            return redirect(url_for('chatting.chat_room'))

        if user.id == chat_room.sender_id:
            chat_room.sender_stay_join = False
        else:
            chat_room.receiver_stay_join = False
            
        db.session.commit()

        return jsonify({"success": True})
        
    except Exception as e:
        db.session.rollback()
        flash(f'채팅방을 나가는 중 오류가 발생했습니다. {e}', 'danger')
        return redirect(url_for('chatting.chat_room'))


# reset_unread_count: 읽지 않은 메시지 수 초기화
@chatting.route('/reset_unread_count', methods=['POST'])
@admin_only
def reset_unread_count():
    data = request.get_json()
    room_id = data.get('room_id')
    chat_room = Room.query.get(room_id)
    current_user_id = User.query.filter_by(name=current_user.name).first().id

    if chat_room:
        if current_user_id == chat_room.sender_id:
            chat_room.sender_unread_count = 0
        else:
            chat_room.receiver_unread_count = 0

        db.session.commit()

        return jsonify({"success": True})
    

# 소켓 연결 확인
@socketio.on("connect")
def test_connect():
    print('connect!')


# 채팅방 접속 업데이트
@socketio.on('join')
def join(data):
    room = data['room_id']
    current_user = data['current_user']

    # 채팅방 접속 시간 업데이트
    chat_room = Room.query.get(room)
    current_user_id = User.query.filter_by(name=current_user).first().id
    
    if current_user_id == chat_room.sender_id:
        chat_room.sender_stay_join = True
    else:
        chat_room.receiver_stay_join = True
        
    db.session.commit()
    join_room(room)


# 메시지 전송
@socketio.on('message')
def handle_message(data):
    room = data['room_id']
    name = data['current_user']
    message = data['message']
    receive_user_name = data['receive_user_name']
    current_time = datetime.now()
    chat_room = Room.query.get(room)

    is_sender = name == chat_room.sender.name

    if is_sender:
        # 수신자의 마지막 접속 시간이 없는 경우 읽지 않은 메시지 수 증가
        if chat_room.receiver_stay_join is False:
            chat_room.receiver_unread_count += 1
    else:
        # 송신자의 마지막 접속 시간이 없는 경우 읽지 않은 메시지 수 증가
        if chat_room.sender_stay_join is False:
            chat_room.sender_unread_count += 1
    
    db.session.commit()
            
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

    # 메시지 전송
    emit('message', {
        'sender_name': new_message.sender_name,
        'text': message, 
        'receive_user_name': receive_user_name,
        'timestamp': current_time.isoformat(),  # 저장된 시간 사용
        'room_id': room
    }, to=room)


# 채팅방 나가기
@socketio.on('leave')
def on_leave(data):
    try:
        room_id = data['room_id']
        user_name = data['current_user']
        
        # 사용자 정보 조회
        user = User.query.filter_by(name=user_name).first()
        if not user:
            # SocketIO 이벤트 핸들러에서는 flash, redirect 등의 함수를 사용할 수 없음
            emit('error', {'success': False, 'message': '사용자를 찾을 수 없습니다.'}, 'danger')
            return jsonify({'success': False})

        # 채팅방 정보 조회
        chat_room = Room.query.get(room_id)
        if not chat_room:
            emit('error', {'success': False, 'message': '채팅방을 찾을 수 없습니다.'}, 'danger')
            return jsonify({'success': False})

        try:
            if user.id == chat_room.sender_id:
                chat_room.sender_join = False
            elif user.id == chat_room.receiver_id:
                chat_room.receiver_join = False
            
            # 두 사용자 모두 채팅방을 나갔을 경우
            if not chat_room.sender_join and not chat_room.receiver_join:
                # 메시지 삭제
                Message.query.filter_by(room_id=chat_room.id).delete()
                # 채팅방 삭제
                db.session.delete(chat_room)
            
            db.session.commit()
            
            # 채팅방 나가기
            leave_room(room_id)
            emit('status', {'success': True, 'data': f"{user_name}님이 나갔습니다."}, to=room_id)
            emit('leave_response', {'success': True, 'message': '채팅방을 성공적으로 나갔습니다.'})
            
        except Exception as e:
            db.session.rollback()
            emit('error', {'success': False, 'message': f'채팅방을 나가는 중 오류가 발생했습니다. {e}'}, 'danger')

    except Exception as e:
        emit('error', {'success': False, 'message': '잘못된 요청입니다.'}, 'danger')

    
# 소켓 연결 해제
@socketio.on('disconnect')
def disconnect(reason):
    print('Client disconnected, reason:', reason)