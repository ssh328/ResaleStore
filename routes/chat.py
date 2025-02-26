from flask import render_template, url_for, request, redirect, Blueprint, make_response, jsonify, flash
from flask_login import current_user
from datetime import datetime
from flask_socketio import SocketIO, join_room, leave_room, emit
from sqlalchemy import or_, and_
from model.data import Room, Message, db, User
from security.security import admin_only
from app import app

# Blueprint for the chat routes
chatting = Blueprint('chatting', __name__, template_folder='templates/chat')

# SocketIO instance
socketio = SocketIO(app, cors_allowed_origins="*")


@chatting.route('/chat_room', methods=['POST', 'GET'])
@admin_only
def chat_room():
    """
    This is the route function that handles the chat room page
    
    Handling POST requests:
    - Creates a new chat room or joins an existing one
    - Checks if a chat room already exists between the two users
    - If no chat room exists, a new one is created
    - If a chat room exists, updates the participation status and last join time
    
    Handling GET requests:
    - Displays the list of chat rooms for the current user
    
    Returns:
        Response: Returns the rendering result of the chat room page
        - Includes cache control headers to ensure the latest data is always displayed
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
    A function that retrieves all chat room information related to the current user
    
    - Retrieve all chat rooms the user is participating in
    - Collect detailed information for each chat room
    
    Returns:
        list: List of chat room information
    """
    user_id = current_user.id
    rooms = Room.query.filter(or_(Room.sender_id == user_id, Room.receiver_id == user_id)).all()
    chat_room_list = []
    
    def get_other_user_info(room):
        """
        # Function to retrieve information about other participants in the chat room
        
        # Identify the current user and the other participant in the chat room
        # Retrieve chat room information
        # Collect information about the other participant
        # Calculate the number of unread messages
        # Retrieve information about the latest message
        # Check the participation status in the chat room

        Returns:
            dict: Returns a dictionary containing the following information:
                - email: Other participant's email
                - receive_user_id: Other participant's user ID
                - room_id: Chat room ID
                - room_check: Chat room participation status
                - receiver_name: Other participant's name
                - latest_message: Content of the latest message
                - message_time: Time of the message
                - other_user_profile: Other participant's profile image
                - unread_count: Number of unread messages
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
    This is a route function that retrieves chat messages and creates a new chat room
    
    Parameters:
        receive_user_id (str): The ID of the user receiving the message
    
    Functionality:
    - Check for existing chat rooms and create a new one if necessary
    - Verify access permissions for the chat room.
    - Update user participation status.
    - Retrieve message history.
    
    Returns:
        JSON: Information about the chat room and messages
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
    Function to update the user's chat room connection status
    
    - Called when leaving the chat room
    - Sets the user's stay_join status to False
    - Checks the existence of the chat room and user
    
    Returns:
        JSON: Success/Failure status
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
    Route function to reset the unread message count
    
    - Called when joining the chat room
    - Resets the counter for the respective sender/receiver only
    
    Returns:
        JSON: Success/Failure status
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
    Event handler to check if the socket connection was successful
    
    - Called when the client connects to the server
    - Prints a message to the console when the connection is successful
    """
    print('connect!')


@socketio.on('join')
def join(data):
    """
    Event handler to update the user's chat room connection status
    
    Parameters:
        data (dict): Data received from the client
            - room_id: Chat room ID
            - current_user: Current user name
    
    - Updates the chat room connection status
    - Joins the user to the specified chat room
    - Sets the stay_join status to True
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
    Event handler to process chat messages
    
    Parameters:
        data (dict): Data received from the client
            - room_id: Chat room ID
            - current_user: Current user name
            - message: Message content
            - receive_user_name: Receiver name
    
    - Updates the unread message count
    - Saves the message to the database
    - Sends the message to other users in the chat room in real time
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
    Event handler called when the user presses the leave chat room button
    
    Parameters:
        data (dict): Data received from the client
            - room_id: Chat room ID
            - current_user: Current user name
    
    - Updates the chat room participation status
    - Deletes the chat room and messages when both users have left
    - Handles the process of leaving the chat room and sends related notifications
    
    Exception handling:
    - If the user or chat room is not found
    - If an error occurs during database processing
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
    Event handler called when the socket connection is disconnected
    
    Parameters:
        reason (str): The reason for the disconnection
    
    - Logs the disconnection of the client
    """
    print('Client disconnected, reason:', reason)