from flask import render_template, url_for, request, redirect, Blueprint, make_response, jsonify, flash
from flask_login import current_user
from datetime import datetime
from flask_socketio import SocketIO, join_room, leave_room, emit
from sqlalchemy import or_, and_
from model.data import Room, Message, db, User
from security.security import admin_only
from app import app

# 채팅 라우트를 위한 Blueprint
chatting = Blueprint('chatting', __name__, template_folder='templates/chat')

# SocketIO 인스턴스
socketio = SocketIO(app, cors_allowed_origins="*")


@chatting.route('/chat_room', methods=['POST', 'GET'])
@admin_only
def chat_room():
    """
    채팅방 페이지를 처리하는 라우트 함수
    
    POST 요청 처리:
    - 새로운 채팅방 생성 또는 기존 채팅방 참여
    - 두 사용자 간의 채팅방이 이미 존재하는지 확인
    - 채팅방이 없으면 새로 생성
    - 채팅방이 있으면 참여 상태와 마지막 참여 시간 업데이트
    
    GET 요청 처리:
    - 현재 사용자의 채팅방 목록 표시
    
    Returns:
        Response: 채팅방 페이지의 렌더링 결과 반환
        - 항상 최신 데이터가 표시되도록 캐시 제어 헤더 포함
    """
    if request.method == 'POST':
        receive_user_id = request.form.get('receive_user_id')
        receive_user_name = request.form.get('receive_user_name')
        current_time = datetime.now()

        room = Room.query.filter(
            or_(
                and_(Room.sender_id == current_user.id, Room.receiver_id == receive_user_id),
                and_(Room.sender_id == receive_user_id, Room.receiver_id == current_user.id)
            )
        ).first()

        if room:
            if current_user.id == room.sender_id and not room.sender_join:
                room.sender_join = True
                room.sender_last_join = current_time
                db.session.commit()
            elif current_user.id == room.receiver_id and not room.receiver_join:
                room.receiver_join = True
                room.receiver_last_join = current_time
                db.session.commit()
        else:
            room = Room(
                sender_id=current_user.id,
                receiver_id=receive_user_id,
                sender_join=True,
                receiver_join=True,
                date=current_time
            )
            db.session.add(room)
            db.session.commit()

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
    
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def get_chat_rooms():
    """
    현재 사용자와 관련된 모든 채팅방 정보를 검색하는 함수
    
    - 사용자가 참여하고 있는 모든 채팅방 검색
    - 각 채팅방에 대한 상세 정보 수집
    
    Returns:
        list: 채팅방 정보 목록
    """
    user_id = current_user.id
    rooms = Room.query.filter(or_(Room.sender_id == user_id, Room.receiver_id == user_id)).all()
    chat_room_list = []
    
    def get_other_user_info(room):
        """
        채팅방의 다른 참여자 정보를 검색하는 함수
        
        - 채팅방에서 현재 사용자와 다른 참여자 식별
        - 채팅방 정보 검색
        - 다른 참여자의 정보 수집
        - 읽지 않은 메시지 수 계산
        - 최신 메시지 정보 검색
        - 채팅방 참여 상태 확인

        Returns:
            dict: 다음 정보를 포함하는 딕셔너리 반환:
                - email: 다른 참여자의 이메일
                - receive_user_id: 다른 참여자의 사용자 ID
                - room_id: 채팅방 ID
                - room_check: 채팅방 참여 상태
                - receiver_name: 다른 참여자의 이름
                - latest_message: 최신 메시지 내용
                - message_time: 메시지 시간
                - other_user_profile: 다른 참여자의 프로필 이미지
                - unread_count: 읽지 않은 메시지 수
        """
        other_user_id = room.receiver_id if room.sender_id == user_id else room.sender_id
        other_user = User.query.get(other_user_id)
        room_check = Room.query.get(room.id)

        is_sender = user_id == room_check.sender_id
        is_receiver = user_id == room_check.receiver_id

        if is_sender:
            unread_count = room_check.sender_unread_count
        elif is_receiver:
            unread_count = room_check.receiver_unread_count
        else:
            unread_count = 0

        latest_message = Message.query.filter_by(room_id=room_check.id).order_by(Message.time.desc()).first()
        message_time = latest_message.time.strftime('%Y-%m-%d') if latest_message else room_check.date.strftime('%Y-%m-%d')
        
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


@chatting.route('/get_messages/<string:receive_user_id>', methods=['GET', 'POST'])
@admin_only
def chat(receive_user_id):
    """
    채팅 메시지를 검색하고 새로운 채팅방을 생성하는 라우트 함수
    
    Parameters:
        receive_user_id (str): 메시지를 받는 사용자의 ID
    
    기능:
    - 기존 채팅방 확인 및 필요한 경우 새로운 채팅방 생성
    - 채팅방 접근 권한 확인
    - 사용자 참여 상태 업데이트
    - 메시지 기록 검색
    
    Returns:
        JSON: 채팅방 및 메시지 정보
    """
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

    chat_room = db.get_or_404(Room, room_id if room_id else room.id)

    if current_user.id != chat_room.sender_id and current_user.id != chat_room.receiver_id:
        flash('채팅방을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('posts.all_products'))
    
    is_sender = current_user.id == chat_room.sender_id
    if is_sender:
        if not chat_room.sender_join:
            chat_room.sender_join = True
            chat_room.sender_last_join = datetime.now()
            db.session.commit()
        last_join_time = chat_room.sender_last_join
    else:
        if not chat_room.receiver_join:
            chat_room.receiver_join = True
            chat_room.receiver_last_join = datetime.now()
            db.session.commit()
        last_join_time = chat_room.receiver_last_join

    messages_query = Message.query.filter_by(room_id=chat_room.id)
    if last_join_time:
        messages_query = messages_query.filter(Message.time >= last_join_time)
    messages = messages_query.order_by(Message.time).all()

    return jsonify({
        'user': current_user.name,
        'room_id': chat_room.id,
        'receive_user_name': receive_user_name,
        'messages': [{
            'id': message.id,
            'room_id': message.room_id,
            'sender_name': message.sender_name,
            'receive_user_name': message.receive_user_name,
            'text': message.text,
            'time': message.time.isoformat()
        } for message in messages],
        'logged_in': current_user.is_authenticated,
        'receive_user_id': receive_user_id,
        'current_user': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email
        }
    })


@chatting.route('/stay_join', methods=['POST'])
@admin_only
def update_stay_join():
    """
    사용자의 채팅방 연결 상태를 업데이트하는 함수
    
    - 채팅방을 나갈 때 호출
    - 사용자의 stay_join 상태를 False로 설정
    - 채팅방과 사용자의 존재 여부 확인
    
    Returns:
        JSON: 성공/실패 상태
    """
    try:
        data = request.get_json()
        room = data.get('room_id')
        current_user = data.get('current_user')
        
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


@chatting.route('/reset_unread_count', methods=['POST'])
@admin_only
def reset_unread_count():
    """
    읽지 않은 메시지 수를 초기화하는 라우트 함수
    
    - 채팅방에 참여할 때 호출
    - 해당 발신자/수신자에 대한 카운터만 초기화
    
    Returns:
        JSON: 성공/실패 상태
    """
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
    """
    소켓 연결이 성공했는지 확인하는 이벤트 핸들러
    
    - 클라이언트가 서버에 연결될 때 호출
    - 연결이 성공하면 콘솔에 메시지 출력
    """
    print('connect!')


@socketio.on('join')
def join(data):
    """
    사용자의 채팅방 연결 상태를 업데이트하는 이벤트 핸들러
    
    Parameters:
        data (dict): 클라이언트로부터 받은 데이터
            - room_id: 채팅방 ID
            - current_user: 현재 사용자 이름
    
    - 채팅방 연결 상태 업데이트
    - 지정된 채팅방에 사용자 참여
    - stay_join 상태를 True로 설정
    """
    room = data['room_id']
    current_user = data['current_user']

    chat_room = Room.query.get(room)
    current_user_id = User.query.filter_by(name=current_user).first().id
    
    if current_user_id == chat_room.sender_id:
        chat_room.sender_stay_join = True
    else:
        chat_room.receiver_stay_join = True
        
    db.session.commit()
    join_room(room)


@socketio.on('message')
def handle_message(data):
    """
    채팅 메시지를 처리하는 이벤트 핸들러
    
    Parameters:
        data (dict): 클라이언트로부터 받은 데이터
            - room_id: 채팅방 ID
            - current_user: 현재 사용자 이름
            - message: 메시지 내용
            - receive_user_name: 수신자 이름
    
    - 읽지 않은 메시지 수 업데이트
    - 데이터베이스에 메시지 저장
    - 채팅방의 다른 사용자에게 실시간으로 메시지 전송
    """
    room = data['room_id']
    name = data['current_user']
    message = data['message']
    receive_user_name = data['receive_user_name']
    current_time = datetime.now()
    chat_room = Room.query.get(room)

    is_sender = name == chat_room.sender.name

    if is_sender:
        if chat_room.receiver_stay_join is False:
            chat_room.receiver_unread_count += 1
    else:
        if chat_room.sender_stay_join is False:
            chat_room.sender_unread_count += 1
    
    db.session.commit()
            
    new_message = Message(
        room_id=room,
        sender_name=name,
        receive_user_name=receive_user_name,
        text=message,
        time=current_time
    )
    db.session.add(new_message)
    db.session.commit()

    emit('message', {
        'sender_name': new_message.sender_name,
        'text': message, 
        'receive_user_name': receive_user_name,
        'timestamp': current_time.isoformat(),
        'room_id': room
    }, to=room)


@socketio.on('leave')
def on_leave(data):
    """
    사용자가 채팅방 나가기 버튼을 눌렀을 때 호출되는 이벤트 핸들러
    
    Parameters:
        data (dict): 클라이언트로부터 받은 데이터
            - room_id: 채팅방 ID
            - current_user: 현재 사용자 이름
    
    - 채팅방 참여 상태 업데이트
    - 두 사용자 모두 나갔을 때 채팅방과 메시지 삭제
    - 채팅방 나가기 처리 및 관련 알림 전송
    
    예외 처리:
    - 사용자나 채팅방을 찾을 수 없는 경우
    - 데이터베이스 처리 중 오류 발생 시
    """
    try:
        room_id = data['room_id']
        user_name = data['current_user']
        
        user = User.query.filter_by(name=user_name).first()
        if not user:
            emit('error', {'success': False, 'message': '사용자를 찾을 수 없습니다.'}, 'danger')
            return jsonify({'success': False})

        chat_room = Room.query.get(room_id)
        if not chat_room:
            emit('error', {'success': False, 'message': '채팅방을 찾을 수 없습니다.'}, 'danger')
            return jsonify({'success': False})

        try:
            if user.id == chat_room.sender_id:
                chat_room.sender_join = False
            elif user.id == chat_room.receiver_id:
                chat_room.receiver_join = False
            
            if not chat_room.sender_join and not chat_room.receiver_join:
                Message.query.filter_by(room_id=chat_room.id).delete()
                db.session.delete(chat_room)
            
            db.session.commit()
            
            leave_room(room_id)
            emit('status', {'success': True, 'data': f"{user_name}님이 나갔습니다."}, to=room_id)
            emit('leave_response', {'success': True, 'message': '채팅방을 성공적으로 나갔습니다.'})
            
        except Exception as e:
            db.session.rollback()
            emit('error', {'success': False, 'message': f'채팅방을 나가는 중 오류가 발생했습니다. {e}'}, 'danger')

    except Exception as e:
        emit('error', {'success': False, 'message': '잘못된 요청입니다.'}, 'danger')

    
@socketio.on('disconnect')
def disconnect(reason):
    """
    소켓 연결이 끊어졌을 때 호출되는 이벤트 핸들러
    
    Parameters:
        reason (str): 연결 종료 이유
    
    - 클라이언트 연결 종료를 로그에 기록
    """
    print('Client disconnected, reason:', reason)