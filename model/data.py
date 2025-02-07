from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase
import uuid


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    profile_image_name = db.Column(db.String(255))

    # 관계 설정: User가 여러 Post에 좋아요를 누를 수 있음
    likes = db.relationship('Like', back_populates='user')

    author_posts = db.relationship("Post", back_populates="author")
    # 일대다 관계를 정의하는 코드, User 와 Post 모델 간의 관계를 설정
    # Post 모델에서 정의된 author 속성과 이 관계를 양방향으로 연결
    # Post 모델에 author 필드에 relationship() 이 정의되어 있어야 함, 두 모델 간의 관계를 상호 참조할 수 있게 됨
    # back_populates: 두 관계를 연결하는 데 사용

    room_sender = db.relationship("Room", foreign_keys="Room.sender_id", back_populates="sender")
    room_receiver = db.relationship("Room", foreign_keys="Room.receiver_id", back_populates="receiver")

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(250), nullable=False)   # 중복 제거 위해 unique=True 제거
    # title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    body = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    like_cnt = db.Column(db.Integer, nullable=False, default=0)

    category = db.Column(db.String(250), nullable=False)

    # 관계 설정: Post가 여러 User로부터 좋아요를 받을 수 있음
    liked_by = db.relationship('Like', back_populates='post')

    # 부모를 참조하는 자식 테이블에 외래키를 배치
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = db.relationship("User", back_populates="author_posts")


class Like(db.Model):
    __tablename__= "likes"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 부모를 참조하는 자식 테이블에 외래키를 배치
    user_email = db.Column(db.String(100), db.ForeignKey('users.email'))
    post_id = db.Column(db.String(36), db.ForeignKey('posts.id'))

    # 관계 설정
    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='liked_by')


class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    # receiver_id은 ForeignKey를 Post 테이블의 author_id로 해야할까?
    # sender, receiver 이렇게 안해도 될듯... 어차피 방 안에 같이 있고 receiver가 sender 에게 대화를 걸 수 있어서...차라리 user1, user2 가 나을듯
    sender_join = db.Column(db.Boolean, nullable=False, default=False)
    receiver_join = db.Column(db.Boolean, nullable=False, default=False)


    # **
    sender_last_join = db.Column(db.DateTime, nullable=True)
    receiver_last_join = db.Column(db.DateTime, nullable=True)
    # **


    # 새로운 필드 추가
    sender_unread_count = db.Column(db.Integer, default=0)
    receiver_unread_count = db.Column(db.Integer, default=0)


    # foreign_keys: 두 개의 외래 키가 같은 테이블을 참조할 때 사용,
    # foreign_keys 를 사용하여 어떤 외래 키가 이 관계에 사용될지를 명확하게 지정해 주어야 함
    sender = db.relationship("User", foreign_keys=[sender_id], back_populates="room_sender")
    receiver = db.relationship("User", foreign_keys=[receiver_id], back_populates="room_receiver")


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_name = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    # sender_email = db.Column(db.String(100), db.ForeignKey('users.email'), nullable=False)
    receive_user_name = db.Column(db.String(36), nullable=False)
    room_id = db.Column(db.String(36), db.ForeignKey('rooms.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    # backref: 빠르게 양방향 참조가 필요할 때 backref 사용
    # back_populates: 양쪽에서 명시적으로 관계를 관리해야 할 때, 복잡한 모델 간의 관계에서는 back_populates 를 권장


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_name = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    review_writer = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

