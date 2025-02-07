from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask import abort, request, flash, redirect, url_for, session
from functools import wraps
from sqlalchemy import or_, and_

from model.data import Room, Post, db

login_manager = LoginManager()


# 관리자 전용 데코레이터
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 인증되지 않은 경우 로그인 페이지로 리다이렉트
        if not current_user.is_authenticated:
            # 현재 요청된 전체 URL을 저장 (쿼리 파라미터 포함)
            next_url = request.path
            flash('You must be signed in first!', 'danger')
            return redirect(url_for('users.login', next=next_url))

        # 인증된 경우 원래 뷰 함수 실행
        return f(*args, **kwargs)
    return decorated_function


# 게시물 작성자 확인 데코레이터
def is_author(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        post_id = kwargs.get('post_id')
        post = db.get_or_404(Post, post_id)
        
        # 로그인하지 않은 경우
        if not current_user.is_authenticated:
            flash('먼저 로그인해주세요!', 'danger')
            return redirect(url_for('users.login'))
            
        # 작성자가 아닌 경우
        if post.author_id != current_user.id:
            flash('해당 게시물에 대한 권한이 없습니다!', 'danger')
            return redirect(url_for('posts.show_post', post_id=post_id))
            
        return f(*args, **kwargs)
    return decorated_function


# 관리자 전용 데코레이터
# def admin_only(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         # 만약 인증된 사용자가 아니라면 403 error 반환
#         # abort 함수로 403 or 404 같은 HTTP 오류를 간단히 반환할 수 있음
#         if not current_user.is_authenticated:
#             return abort(403)

#         # 그렇지 않으면 경로 기능 수행
#         return f(*args, **kwargs)
#     return decorated_function

def chat_room_exists(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # kwargs에서 receive_user_id를 가져옴
        receive_user_id = kwargs.get('receive_user_id')

        # 채팅방 존재 여부 확인 (current_user와 receive_user_id로 필터링)
        chat_room = Room.query.filter(
            or_(
                and_(Room.sender_id == current_user.id, Room.receiver_id == receive_user_id),
                and_(Room.sender_id == receive_user_id, Room.receiver_id == current_user.id),
            )
        ).first()

        if chat_room is None or (chat_room.sender_join is False and chat_room.sender_id == current_user.id) or (chat_room.receiver_join is False and chat_room.receiver_id == current_user.id):
            # 채팅방이 없거나, 현재 사용자가 방을 나간 경우 404 오류 반환
            flash('존재하지 않는 채팅방입니다!', 'danger')
            return redirect(url_for('users.chat_room'))

        # 채팅방이 존재할 경우 원래 뷰 함수 실행
        return f(*args, **kwargs)
    return decorated_function
