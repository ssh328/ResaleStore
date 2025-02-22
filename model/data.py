from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase
import uuid


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# 사용자 모델
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    profile_image_name = db.Column(db.String(255))

    # 양방향 관계 설정
    likes = db.relationship('Like', back_populates='user')
    author_posts = db.relationship("Post", back_populates="author")
    room_sender = db.relationship("Room", foreign_keys="Room.sender_id", back_populates="sender")
    room_receiver = db.relationship("Room", foreign_keys="Room.receiver_id", back_populates="receiver")


# 게시물 모델
class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(250), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    body = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    like_cnt = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(250), nullable=False)

    # 외래키 설정
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # 양방향 관계 설정
    liked_by = db.relationship('Like', back_populates='post')
    author = db.relationship("User", back_populates="author_posts")


# 좋아요 모델
class Like(db.Model):
    __tablename__= "likes"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 외래키 설정
    user_email = db.Column(db.String(100), db.ForeignKey('users.email'))
    post_id = db.Column(db.String(36), db.ForeignKey('posts.id'))

    # 양방향 관계 설정
    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='liked_by')


# 채팅방 모델
class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    sender_last_join = db.Column(db.DateTime, nullable=True)
    receiver_last_join = db.Column(db.DateTime, nullable=True)
    sender_unread_count = db.Column(db.Integer, default=0)
    receiver_unread_count = db.Column(db.Integer, default=0)

    # '나가기 버튼' 누르기 전 방을 나가지 않은 상태를 표시하기 위해 사용
    sender_join = db.Column(db.Boolean, nullable=False, default=False)
    receiver_join = db.Column(db.Boolean, nullable=False, default=False)

    # 채팅방을 클릭해서 접속 중일 때, 그리고 접속이 끊겼을 때 확인하기 위해 사용
    sender_stay_join = db.Column(db.Boolean, nullable=False, default=False)
    receiver_stay_join = db.Column(db.Boolean, nullable=False, default=False)

    # 양방향 관계 설정
    sender = db.relationship("User", foreign_keys=[sender_id], back_populates="room_sender")
    receiver = db.relationship("User", foreign_keys=[receiver_id], back_populates="room_receiver")


# 메시지 모델
class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_name = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    receive_user_name = db.Column(db.String(36), nullable=False)
    room_id = db.Column(db.String(36), db.ForeignKey('rooms.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)


# 리뷰 모델
class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_name = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    review_writer = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)