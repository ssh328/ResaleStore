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
            flash('먼저 로그인해주세요!', 'danger')
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