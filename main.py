from flask import render_template, jsonify
from flask_login import current_user
from dotenv import load_dotenv
import os

from security.security import login_manager
from routes.chat import socketio
from app import app
from model.data import db, User, Post, Like
from routes.users import users
from routes.posts import posts
from routes.chat import chatting

# .env 파일에서 환경 변수를 프로세스의 환경 변수로 로드하기 위해 python-dotenv 라이브러리를 사용
load_dotenv()


# 환경 변수에서 비밀 키 설정
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Flask_Login
login_manager.init_app(app)


# 환경 변수에서 데이터베이스 URI 설정
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
# SQLAlchemy 수정 추적 비활성화
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy 초기화
db.init_app(app)


# 데이터베이스 생성
with app.app_context():
    db.create_all()


# Login management
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

# Main page
@app.route('/')
def home():
    return render_template('home.html', logged_in=current_user.is_authenticated)


# 블루프린트 등록
app.register_blueprint(users, url_prefix='/')
app.register_blueprint(posts, url_prefix='/posts')
app.register_blueprint(chatting, url_prefix='/chat')


@app.route('/increase/<string:post_id>', methods=["POST"])
def increase(post_id):
    """
    주어진 post_id의 좋아요 상태 토글
    사용자가 이미 좋아요를 눌렀으면 좋아요 제거, 그렇지 않으면 좋아요 추가
    게시물의 좋아요 수가 업데이트되고 JSON 형식으로 반환
    """
    post = db.get_or_404(Post, post_id)

    like = Like.query.filter_by(user_email=current_user.email, post_id=post_id).first()

    if like:
        db.session.delete(like)
        post.like_cnt -= 1

    else:
        new_like = Like(user_email=current_user.email, post_id=post_id)
        db.session.add(new_like)
        post.like_cnt += 1

    db.session.commit()

    return jsonify({
        'like_cnt': post.like_cnt
        })


if __name__ == '__main__' :
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)