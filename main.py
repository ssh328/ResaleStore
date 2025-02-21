from flask import render_template, jsonify
from flask_login import current_user
from dotenv import load_dotenv
import os

from security.security import login_manager, admin_only
from routes.chat import socketio


# app
from app import app

# data 모델
from model.data import db, User, Post, Like, Room, Message

# users 루트
from routes.users import users

# posts 루트
from routes.posts import posts

# chat 루트
from routes.chat import chatting

# .env 파일에 정의된 환경 변수를 로드하는 함수
load_dotenv()

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Flask_Login
login_manager.init_app(app)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy 초기화
db.init_app(app)


# 데이터 베이스 생성
with app.app_context():
    db.create_all()


# 로그인 관리
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

# 메인 페이지
@app.route('/')
def home():
    return render_template('home.html', logged_in=current_user.is_authenticated)


# 블루프린트 등록
app.register_blueprint(users, url_prefix='/')
app.register_blueprint(posts, url_prefix='/posts')
app.register_blueprint(chatting, url_prefix='/chat')


# 좋아요 버튼 누르면 1씩 증가
# 서버에서 JavaScript로 데이터 전달 하기 위해 url 생성
@app.route('/increase/<string:post_id>', methods=["POST"])
def increase(post_id):
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
    # jsonify(): 서버에서 JSON 형식의 응답을 클라이언트에게 반환할 때 사용
    # Python 딕셔너리 {'data_counter': counter} 를 JSON 형식으로 반환


if __name__ == '__main__' :
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)