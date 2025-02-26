from flask_login import LoginManager, current_user
from flask import request, flash, redirect, url_for
from functools import wraps

from model.data import Post, db

# Create an instance of Flask-Login's LoginManager
login_manager = LoginManager()


def admin_only(f):
    """
    If the user is not authenticated, redirect to the login page
    If the user is authenticated, execute the original view function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            next_url = request.path
            flash('먼저 로그인해주세요!', 'danger')
            return redirect(url_for('users.login', next=next_url))

        return f(*args, **kwargs)
    return decorated_function


def is_author(f):
    """
    If the user is not authenticated, redirect to the login page
    If the user is authenticated, execute the original view function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        post_id = kwargs.get('post_id')
        post = db.get_or_404(Post, post_id)
        
        if not current_user.is_authenticated:
            flash('먼저 로그인해주세요!', 'danger')
            return redirect(url_for('users.login'))
            
        if post.author_id != current_user.id:
            flash('해당 게시물에 대한 권한이 없습니다!', 'danger')
            return redirect(url_for('posts.show_post', post_id=post_id))
            
        return f(*args, **kwargs)
    return decorated_function